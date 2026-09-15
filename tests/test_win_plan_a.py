"""Workstream A (docs/WIN_PLAN.md) endpoint tests: groundedness judge (A1),
retrieval ablation (A2), compare cache (A3), offline fallback (A4).

Uses unique X-Forwarded-For per test + limiter reset (same pattern as
tests/test_resilience_tracing.py) so /predict rate limits never flake.
"""
import sys
import uuid

sys.path.insert(0, r"C:\Hiver")

import pytest
from fastapi.testclient import TestClient

import backend.main as app_mod

PROBES = [
    ("my train from Euston to Manchester is delayed by 40 mins, can I get compensation?",
     "Sorry your train was delayed. You may be entitled to Delay Repay compensation. DM us your booking ref so we can help."),
    ("is the 21:03 train from Euston to Birmingham International still running?",
     "Let's check your service. Check live departures, then DM us your from/to and date/time."),
    ("Wow this train from Oxford to Stockport is ridiculously packed",
     "Sorry about your experience. Please share what happened and DM us so we can log it."),
    ("Why have i never recieved my refund on tickets had this problem a few times now",
     "We can help with your amendment or refund. Check your ticket terms, then DM us your booking ref."),
    ("my email is jane.doe@example.com, please help with my ticket",
     "We can point you in the right direction. DM us your journey details and we will explain the options."),
]


@pytest.fixture()
def tclient(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HIVER_OFFLINE", raising=False)
    try:
        if app_mod.limiter is not None:
            app_mod.limiter._storage.reset()
    except Exception:
        pass
    c = TestClient(app_mod.app)
    yield c
    try:
        if app_mod.limiter is not None:
            app_mod.limiter._storage.reset()
    except Exception:
        pass


def _ip():
    return {"X-Forwarded-For": f"win-a-{uuid.uuid4().hex[:8]}"}


def test_groundedness_schema_on_probes(tclient):
    for text, reply in PROBES:
        r = tclient.post("/judge/groundedness",
                         json={"brand": "virgin", "text": text, "reply": reply})
        assert r.status_code == 200, r.text[:200]
        obj = r.json()
        assert set(obj) >= {"claims", "score", "model"}, obj.keys()
        assert isinstance(obj["claims"], list) and len(obj["claims"]) >= 1
        for cl in obj["claims"]:
            assert set(cl) >= {"text", "supported", "passage_id"}, cl
            assert isinstance(cl["supported"], bool)
        assert 0.0 <= obj["score"] <= 1.0
        assert obj["model"] == "heuristic-offline"  # no key in test env


def test_groundedness_empty_reply(tclient):
    r = tclient.post("/judge/groundedness",
                     json={"brand": "virgin", "text": "hello?", "reply": ""})
    assert r.status_code == 200
    assert r.json()["claims"] == [] and r.json()["score"] == 0.0


def test_groundedness_pinned_passages(tclient):
    text, reply = PROBES[0]
    first = tclient.post("/judge/groundedness",
                         json={"brand": "virgin", "text": text, "reply": reply}).json()
    pinned = [c["passage_id"] for c in first["claims"] if c["passage_id"]]
    assert pinned, "pilot probe should support >=1 claim for pin test"
    r = tclient.post("/judge/groundedness",
                     json={"brand": "virgin", "text": text, "reply": reply,
                           "passage_ids": pinned[:1]})
    assert r.status_code == 200
    for cl in r.json()["claims"]:
        if cl["supported"]:
            assert cl["passage_id"] in pinned[:1]


def test_ablation_default_arms(tclient):
    r = tclient.post("/eval/retrieval-ablation", json={})
    assert r.status_code == 200, r.text[:300]
    obj = r.json()
    assert obj["brand"] == "virgin" and obj["n"] == 60
    assert len(obj["arms"]) == 8
    names = {a["name"] for a in obj["arms"]}
    assert names == {f"{arm}:k={k}:ctx={cw}" for arm in ("keyword", "virgin_nn")
                     for k in (1, 5) for cw in (0, 2)}
    for a in obj["arms"]:
        for k in ("recall_proxy", "groundedness_mean", "groundedness_ge4_rate",
                  "ge4_rate", "p50_ms", "p95_ms", "support_rate", "n"):
            assert k in a, (a.get("name"), k)
        assert 0.0 <= a["recall_proxy"] <= 1.0
        assert 1.0 <= a["groundedness_mean"] <= 5.0


def test_ablation_rejects_unknown_arm(tclient):
    r = tclient.post("/eval/retrieval-ablation", json={"arms": ["nope"]})
    assert r.status_code == 400
    assert r.json().get("title") == "Bad Request"


def test_compare_matches_docs(tclient):
    r = tclient.get("/eval/compare", params={"brands": "virgin,apple"})
    assert r.status_code == 200, r.text[:200]
    obj = r.json()
    assert set(obj) >= {"results", "cached"}
    v, a = obj["results"]["virgin"], obj["results"]["apple"]
    # Virgin: evaluation/virgin/BASELINE_VS_FINAL.md §B final row (n=200).
    assert (v["intent_acc"], v["macro_f1"], v["esc_f1"], v["ground_mean"], v["n"]) == \
        (0.795, 0.803, 0.767, 4.21, 200)
    # Apple: evaluation/BASELINE_VS_FINAL.md §B final row (n=60; ground_mean from
    # the documented offline human-60 pass, within rounding of §A 4.75).
    assert (a["intent_acc"], a["macro_f1"], a["esc_f1"], a["n"]) == (0.433, 0.443, 0.471, 60)
    assert abs(a["ground_mean"] - 4.75) < 0.05
    assert obj["latency_ms"] < 2000  # cache-hit budget


def test_compare_rejects_unknown_brand(tclient):
    r = tclient.get("/eval/compare", params={"brands": "virgin,ebay"})
    assert r.status_code == 400


def test_predict_offline_flag_no_llm(tclient, monkeypatch):
    from src import groq_draft as gd

    def _boom(*a, **k):
        raise AssertionError("Groq must not be called in offline mode")

    monkeypatch.setattr(gd, "draft_with_groq", _boom)
    r = tclient.post("/predict",
                     json={"text": "my train was delayed, refund please",
                           "brand": "virgin", "offline": True},
                     headers=_ip())
    assert r.status_code == 200, r.text[:200]
    obj = r.json()
    assert obj["offline"] is True
    assert obj["draft_path"] == "template"
    rec = tclient.get(f"/inspect/{obj['request_id']}").json()
    assert rec["offline"] is True


def test_predict_online_echoes_offline_false(tclient):
    r = tclient.post("/predict",
                     json={"text": "my train was delayed, refund please", "brand": "virgin"},
                     headers=_ip())
    assert r.status_code == 200
    assert r.json()["offline"] is False


def test_predict_offline_env(tclient, monkeypatch):
    from src import groq_draft as gd

    def _boom(*a, **k):
        raise AssertionError("Groq must not be called in offline mode")

    monkeypatch.setattr(gd, "draft_with_groq", _boom)
    monkeypatch.setenv("HIVER_OFFLINE", "1")
    r = tclient.post("/predict",
                     json={"text": "my train was delayed, refund please", "brand": "virgin"},
                     headers=_ip())
    assert r.status_code == 200
    assert r.json()["offline"] is True
