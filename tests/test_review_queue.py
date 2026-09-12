"""Phase 3 HITL review queue: transitions, idempotency, audit, matrix, API smoke."""
import sys

sys.path.insert(0, r"C:\Hiver")

import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    p = tmp_path / "review_queue_test.db"
    monkeypatch.setenv("HIVER_REVIEW_DB", str(p))
    from src import review_store as rs
    rs.init_db(str(p))
    return str(p)


def _enq(rs, **kw):
    base = dict(brand="virgin", intent="delay_claim", intent_confidence=0.9,
                text="My train was delayed, refund please", draft_reply="Draft reply here",
                grounding_passage_ids=["1"], reason_code="money_review", signals={})
    base.update(kw)
    return rs.enqueue(**base)


def test_state_transitions(tmp_db):
    from src import review_store as rs
    row = _enq(rs, db_path=tmp_db)
    assert row["status"] == "PENDING"
    ok = rs.transition(row["id"], "APPROVED", reviewer="alice", rationale="looks good",
                       db_path=tmp_db)
    assert ok["status"] == "APPROVED"
    assert ok["reviewer"] == "alice"
    with pytest.raises(ValueError):
        rs.transition(row["id"], "REJECTED", reviewer="bob", db_path=tmp_db)

    row2 = _enq(rs, text="other text here", db_path=tmp_db)
    with pytest.raises(ValueError):
        rs.transition(row2["id"], "APPROVED_WITH_EDITS", reviewer="a",
                      rationale="x", final_text="  ", db_path=tmp_db)
    ed = rs.transition(row2["id"], "APPROVED_WITH_EDITS", reviewer="a", rationale="fix",
                       final_text="Fixed reply", corrected_intent="fare_ticketing",
                       db_path=tmp_db)
    assert ed["status"] == "APPROVED_WITH_EDITS"
    assert ed["final_text"] == "Fixed reply"
    assert ed["corrected_intent"] == "fare_ticketing"
    assert ed["final_hash"] != ed["orig_hash"]

    row3 = _enq(rs, text="third text", db_path=tmp_db)
    rej = rs.transition(row3["id"], "REJECTED", reviewer="mod", rationale="spam",
                        db_path=tmp_db)
    assert rej["status"] == "REJECTED"
    with pytest.raises(ValueError):
        rs.transition(row3["id"], "APPROVED", reviewer="x", db_path=tmp_db)
    with pytest.raises(ValueError):
        rs.transition(row3["id"], "BOGUS", reviewer="x", db_path=tmp_db)


def test_expire_overdue(tmp_db):
    from src import review_store as rs
    row = _enq(rs, sla_minutes=1, db_path=tmp_db)
    # Force SLA into the past, then sweep.
    import sqlite3
    conn = sqlite3.connect(tmp_db)
    conn.execute("UPDATE escalations SET sla_due_at='2000-01-01T00:00:00+00:00' WHERE id=?",
                 (row["id"],))
    conn.commit()
    conn.close()
    n = rs.expire_overdue(db_path=tmp_db)
    assert n >= 1
    got = rs.get_escalation(row["id"], db_path=tmp_db)
    assert got["status"] == "EXPIRED"


def test_idempotency(tmp_db):
    from src import review_store as rs
    a = _enq(rs, idempotency_key="k-123", db_path=tmp_db)
    b = _enq(rs, idempotency_key="k-123", text="DIFFERENT", db_path=tmp_db)
    assert a["id"] == b["id"]
    assert b["_deduped"] is True
    items = rs.list_queue(db_path=tmp_db)
    assert sum(1 for i in items if i.get("idempotency_key") == "k-123") == 1


def test_audit_append_only(tmp_db):
    from src import review_store as rs
    row = _enq(rs, db_path=tmp_db)
    rs.transition(row["id"], "APPROVED", reviewer="alice", rationale="ok", db_path=tmp_db)
    evs = rs.list_audit(row["id"], db_path=tmp_db)
    assert [e["event"] for e in evs] == ["CREATED", "APPROVED"]
    assert evs[1]["reviewer"] == "alice"
    assert evs[1]["rationale"] == "ok"
    assert evs[1]["orig_hash"] and evs[1]["final_hash"] and evs[1]["ts"]
    # No update/delete path exists: audit rows are insert-only via API surface.
    assert all(set(e) >= {"orig_hash", "final_hash", "reviewer", "rationale", "ts"}
               for e in evs)


def test_enqueue_from_result_one_call(tmp_db):
    from src import review_store as rs

    class R:
        intent = "delay_claim"
        intent_confidence = 0.92
        draft_reply = "draft"
        grounding_passage_ids = ["7"]
        decision = "escalate"
        escalate_reason = "money_review"
        escalate_signals = {"brand": "virgin"}

    row = rs.enqueue_from_result(R(), "delayed 2hrs, refund £20", "virgin", db_path=tmp_db)
    assert row["enqueued"] is True and row["status"] == "PENDING"

    class A(R):
        decision = "auto_handle"

    assert rs.enqueue_from_result(A(), "thanks!", "virgin", db_path=tmp_db)["enqueued"] is False


def test_matrix_routing_determinism():
    from src import review_store as rs
    m = rs.load_matrix()
    # Deterministic: repeated calls agree.
    for _ in range(3):
        assert rs.route_for("delay_claim", 0.95, m) == "must_review"
        assert rs.route_for("howto_guidance", 0.9, m) == "auto"
        assert rs.route_for("fare_ticketing", 0.5, m) == "review"
        assert rs.route_for("delay_claim", 0.2, m) == "must_review"
    # High-risk money/safety is must_review at ANY confidence.
    for conf in (0.1, 0.5, 0.95):
        assert rs.route_for("ticket_change_refund", conf, m) == "must_review"
        assert rs.route_for("purchase_billing_service", conf, m) == "must_review"
    # Warm-transfer payload shape.
    wt = rs.build_warm_transfer({"id": "x", "brand": "virgin", "text": "t",
                                 "intent": "delay_claim", "intent_confidence": 0.8,
                                 "reason_code": "money_review", "draft_reply": "d",
                                 "grounding_passage_ids": ["1"],
                                 "sla_due_at": "s", "status": "PENDING",
                                 "created_at": "c"})
    assert set(wt) >= {"transcript", "intent", "reason_code", "draft", "next_step", "sla_due_at"}


def test_api_smoke_both_brands(tmp_db):
    from backend.main import app
    c = TestClient(app)
    # Existing routes unchanged.
    for brand in ("virgin", "apple"):
        r = c.post("/predict", json={"text": "Hello, need help with my booking", "brand": brand})
        assert r.status_code == 200, r.text
        body = r.json()
        assert set(body) >= {"request_id", "brand", "intent", "intent_confidence",
                             "draft_reply", "decision", "escalate_reason", "latency_ms"}
    m = c.get("/metrics")
    assert m.status_code == 200 and "predict_count" in m.json()

    # New review endpoints: enqueue escalations for both brands.
    v = c.post("/review/enqueue", json={"text": "My train was delayed 2 hours, refund my £50 ticket now",
                                        "brand": "virgin"})
    assert v.status_code == 200, v.text
    assert v.json()["enqueued"] is True
    vid = v.json()["id"]

    a = c.post("/review/enqueue", json={"text": "I want a human now, hacked account",
                                        "brand": "apple"})
    assert a.status_code == 200, a.text
    assert a.json()["enqueued"] is True
    aid = a.json()["id"]

    q = c.get("/review/queue", params={"status": "PENDING"})
    assert q.status_code == 200 and q.json()["count"] >= 2

    t = c.get(f"/review/{vid}/transfer")
    assert t.status_code == 200
    assert set(t.json()) >= {"transcript", "intent", "reason_code", "draft", "next_step", "sla_due_at"}

    au = c.get(f"/review/{vid}/audit")
    assert au.status_code == 200 and au.json()["events"][0]["event"] == "CREATED"

    ok = c.post(f"/review/{vid}/approve", json={"reviewer": "smoke", "rationale": "ok"})
    assert ok.status_code == 200 and ok.json()["status"] == "APPROVED"

    ed = c.post(f"/review/{aid}/edit",
                json={"reviewer": "smoke", "rationale": "fix",
                      "final_text": "Edited reply for smoke test."})
    assert ed.status_code == 200 and ed.json()["status"] == "APPROVED_WITH_EDITS"

    # Terminal double-decide is a 409, unknown id is a 404.
    assert c.post(f"/review/{vid}/reject", json={"reviewer": "x"}).status_code == 409
    assert c.get("/review/does-not-exist").status_code == 404

    mx = c.get("/review/matrix")
    assert mx.status_code == 200 and mx.json()["matrix"]["version"] >= 1
    st = c.get("/review/stats")
    assert st.status_code == 200 and st.json()["total"] >= 2

    # Idempotent enqueue via key.
    k1 = c.post("/review/enqueue", json={"text": "My train was delayed 2 hours, refund my £50 ticket now",
                                         "brand": "virgin", "idempotency_key": "smoke-key-1"})
    k2 = c.post("/review/enqueue", json={"text": "My train was delayed 2 hours, refund my £50 ticket now",
                                         "brand": "virgin", "idempotency_key": "smoke-key-1"})
    assert k1.json()["id"] == k2.json()["id"]
