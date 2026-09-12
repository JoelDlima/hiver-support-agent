"""HITL review queue store (Phase 3).

SQLite-backed escalation inbox:
  PENDING -> APPROVED | APPROVED_WITH_EDITS | REJECTED | EXPIRED

- One-call enqueue from agent.handle results (decision == "escalate").
- Idempotency keys (UNIQUE): repeat enqueue with the same key returns the
  existing row instead of duplicating.
- Attestation audit trail (append-only): every state change appends an event
  with {orig_hash, final_hash, reviewer, rationale, ts}.
- Warm-transfer payload builder for handoff to a human agent.
- Autonomy-matrix routing helper (intent x risk-tier x confidence-band).

DB location: data/processed/review_queue.db (override with HIVER_REVIEW_DB env).
The file itself is runtime state (gitignored); schema is created on demand.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = ROOT / "data" / "processed" / "review_queue.db"
MATRIX_PATH = ROOT / "autonomy_matrix.yaml"

STATUSES = ("PENDING", "APPROVED", "APPROVED_WITH_EDITS", "REJECTED", "EXPIRED")
TERMINAL = ("APPROVED", "APPROVED_WITH_EDITS", "REJECTED", "EXPIRED")
ALLOWED = {
    "PENDING": ("APPROVED", "APPROVED_WITH_EDITS", "REJECTED", "EXPIRED"),
}
ROUTES = ("auto", "review", "must_review")

# Fallback risk tiers (used when autonomy_matrix.yaml is absent/unparseable).
_FALLBACK_HIGH = {
    "delay_claim", "ticket_change_refund", "complaint_service",
    "accessibility_assistance", "apple_id_icloud", "purchase_billing_service",
    "hardware_device", "setup_transfer_restore",
}
_FALLBACK_MEDIUM = {"fare_ticketing", "timetable_platform", "lost_property"}

_NEXT_STEP_BY_REASON = {
    "legal_safety": "Safety triage first: confirm no one is at risk, then follow the complaint/safety playbook.",
    "account_security": "Verify identity via DM before any account action; never ask for passwords publicly.",
    "pii_review": "Remove/avoid PII in public reply; continue over DM only.",
    "human_request": "Acknowledge and route to a human agent; confirm DM channel.",
    "money_review": "Double-check fare/refund terms before quoting anything; no invented prices.",
    "money_threshold": "Below money-confidence bar — human confirms fare/refund wording.",
    "complaint_review": "Apologise, log service/date/time, escalate per complaint playbook.",
    "unresolvable": "Ask one clarifying question (journey + date/time) or route to human.",
    "unresolvable-language": "Reply in English; ask the customer to resend in English or route to language support.",
}


def get_db_path(db_path: str | Path | None = None) -> Path:
    if db_path:
        return Path(db_path)
    env = os.environ.get("HIVER_REVIEW_DB")
    if env:
        return Path(env)
    return DEFAULT_DB_PATH


def _now_iso() -> str:
    try:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()
    except Exception:
        return datetime.datetime.utcnow().isoformat() + "+00:00"


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def _connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    p = get_db_path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p), check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
    except Exception:
        pass
    return conn


def init_db(db_path: str | Path | None = None) -> Path:
    p = get_db_path(db_path)
    conn = _connect(p)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS escalations (
                id TEXT PRIMARY KEY,
                brand TEXT NOT NULL,
                intent TEXT NOT NULL,
                intent_confidence REAL NOT NULL,
                text TEXT NOT NULL,
                draft_reply TEXT NOT NULL DEFAULT '',
                grounding_passage_ids TEXT NOT NULL DEFAULT '[]',
                decision TEXT NOT NULL DEFAULT 'escalate',
                reason_code TEXT NOT NULL DEFAULT 'unresolvable',
                signals TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'PENDING',
                reviewer TEXT,
                rationale TEXT,
                final_text TEXT,
                corrected_intent TEXT,
                orig_hash TEXT NOT NULL,
                final_hash TEXT,
                idempotency_key TEXT UNIQUE,
                sla_due_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                reviewed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                escalation_id TEXT NOT NULL REFERENCES escalations(id),
                event TEXT NOT NULL,
                reviewer TEXT,
                rationale TEXT,
                orig_hash TEXT,
                final_hash TEXT,
                ts TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_esc_status ON escalations(status);
            CREATE INDEX IF NOT EXISTS idx_esc_brand ON escalations(brand);
            CREATE INDEX IF NOT EXISTS idx_esc_idem ON escalations(idempotency_key);
            CREATE INDEX IF NOT EXISTS idx_audit_esc ON audit_events(escalation_id);
            """
        )
        # Light migration for DBs created before corrected_intent existed.
        try:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(escalations)").fetchall()]
            if "corrected_intent" not in cols:
                conn.execute("ALTER TABLE escalations ADD COLUMN corrected_intent TEXT")
        except Exception:
            pass
        conn.commit()
    finally:
        conn.close()
    return p


def _row_to_dict(r: sqlite3.Row) -> dict:
    d = dict(r)
    for k in ("grounding_passage_ids", "signals"):
        v = d.get(k)
        if isinstance(v, str):
            try:
                d[k] = json.loads(v)
            except Exception:
                d[k] = [] if k == "grounding_passage_ids" else {}
    return d


def _append_audit(
    conn: sqlite3.Connection,
    escalation_id: str,
    event: str,
    reviewer: str | None,
    rationale: str,
    orig_hash: str | None,
    final_hash: str | None,
    ts: str,
) -> None:
    conn.execute(
        "INSERT INTO audit_events (escalation_id, event, reviewer, rationale, orig_hash, final_hash, ts)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (escalation_id, event, reviewer, rationale or "", orig_hash, final_hash, ts),
    )


def enqueue(
    *,
    brand: str,
    intent: str,
    intent_confidence: float,
    text: str,
    draft_reply: str = "",
    grounding_passage_ids: list | None = None,
    reason_code: str = "unresolvable",
    signals: dict | None = None,
    idempotency_key: str | None = None,
    sla_minutes: int | None = None,
    db_path: str | Path | None = None,
) -> dict:
    """Insert a new PENDING escalation. Idempotent on idempotency_key."""
    init_db(db_path)
    conn = _connect(db_path)
    try:
        if idempotency_key:
            row = conn.execute(
                "SELECT * FROM escalations WHERE idempotency_key = ?", (idempotency_key,)
            ).fetchone()
            if row:
                d = _row_to_dict(row)
                d["_deduped"] = True
                return d
        now = _now_iso()
        try:
            sla_min = int(sla_minutes) if sla_minutes is not None else 30
        except Exception:
            sla_min = 30
        sla_min = max(1, min(sla_min, 24 * 60))
        try:
            due = (
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(minutes=sla_min)
            ).isoformat()
        except Exception:
            due = now
        eid = uuid.uuid4().hex[:12]
        # Collision-proof id generation.
        for _ in range(3):
            exists = conn.execute("SELECT 1 FROM escalations WHERE id = ?", (eid,)).fetchone()
            if not exists:
                break
            eid = uuid.uuid4().hex[:12]
        orig_hash = sha256_text(draft_reply or "")
        conn.execute(
            "INSERT INTO escalations (id, brand, intent, intent_confidence, text, draft_reply,"
            " grounding_passage_ids, decision, reason_code, signals, status,"
            " orig_hash, idempotency_key, sla_due_at, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, 'escalate', ?, ?, 'PENDING', ?, ?, ?, ?, ?)",
            (
                eid,
                (brand or "virgin").lower().strip(),
                intent or "other_out_of_scope",
                float(intent_confidence or 0.0),
                text or "",
                draft_reply or "",
                json.dumps(list(grounding_passage_ids or [])),
                reason_code or "unresolvable",
                json.dumps(dict(signals or {})),
                orig_hash,
                idempotency_key,
                due,
                now,
                now,
            ),
        )
        _append_audit(conn, eid, "CREATED", None, reason_code or "unresolvable",
                      orig_hash, None, now)
        conn.commit()
        row = conn.execute("SELECT * FROM escalations WHERE id = ?", (eid,)).fetchone()
        d = _row_to_dict(row)
        d["_deduped"] = False
        return d
    finally:
        conn.close()


def enqueue_from_result(
    result,
    text: str = "",
    brand: str | None = None,
    *,
    idempotency_key: str | None = None,
    sla_minutes: int | None = None,
    db_path: str | Path | None = None,
    force: bool = False,
) -> dict:
    """One-call enqueue for agent.handle results with decision == 'escalate'.

    Returns {"enqueued": False, ...} for non-escalations unless force=True.
    """
    decision = getattr(result, "decision", "escalate")
    if decision != "escalate" and not force:
        return {"enqueued": False, "decision": decision}
    b = brand or getattr(result, "brand", None) or (result.escalate_signals or {}).get("brand", "virgin")
    row = enqueue(
        brand=b,
        intent=getattr(result, "intent", "other_out_of_scope"),
        intent_confidence=float(getattr(result, "intent_confidence", 0.0) or 0.0),
        text=text if text else "",
        draft_reply=getattr(result, "draft_reply", "") or "",
        grounding_passage_ids=list(getattr(result, "grounding_passage_ids", []) or []),
        reason_code=getattr(result, "escalate_reason", "unresolvable") or "unresolvable",
        signals=dict(getattr(result, "escalate_signals", {}) or {}),
        idempotency_key=idempotency_key,
        sla_minutes=sla_minutes,
        db_path=db_path,
    )
    row["enqueued"] = True
    return row


def get_escalation(escalation_id: str, db_path: str | Path | None = None) -> dict | None:
    init_db(db_path)
    conn = _connect(db_path)
    try:
        row = conn.execute("SELECT * FROM escalations WHERE id = ?", (escalation_id,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def list_queue(
    *,
    status: str | None = None,
    brand: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db_path: str | Path | None = None,
) -> list[dict]:
    init_db(db_path)
    conn = _connect(db_path)
    try:
        q = "SELECT * FROM escalations"
        clauses, params = [], []
        if status:
            clauses.append("status = ?")
            params.append(status)
        if brand:
            clauses.append("brand = ?")
            params.append(brand.lower().strip())
        if clauses:
            q += " WHERE " + " AND ".join(clauses)
        q += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params += [max(1, min(int(limit or 100), 500)), max(0, int(offset or 0))]
        return [_row_to_dict(r) for r in conn.execute(q, params).fetchall()]
    finally:
        conn.close()


def list_audit(escalation_id: str, db_path: str | Path | None = None) -> list[dict]:
    init_db(db_path)
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM audit_events WHERE escalation_id = ? ORDER BY id ASC",
            (escalation_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def transition(
    escalation_id: str,
    to_status: str,
    *,
    reviewer: str = "reviewer",
    rationale: str = "",
    final_text: str | None = None,
    corrected_intent: str | None = None,
    db_path: str | Path | None = None,
) -> dict:
    """PENDING -> APPROVED | APPROVED_WITH_EDITS | REJECTED | EXPIRED + audit."""
    if to_status not in STATUSES or to_status == "PENDING":
        raise ValueError(f"invalid target status: {to_status}")
    init_db(db_path)
    conn = _connect(db_path)
    try:
        row = conn.execute("SELECT * FROM escalations WHERE id = ?", (escalation_id,)).fetchone()
        if not row:
            raise KeyError(f"unknown escalation: {escalation_id}")
        cur = _row_to_dict(row)
        if cur["status"] != "PENDING":
            raise ValueError(f"terminal state {cur['status']}: no further transitions")
        if to_status not in ALLOWED["PENDING"]:
            raise ValueError(f"transition PENDING -> {to_status} not allowed")
        if to_status == "APPROVED_WITH_EDITS" and not (final_text or "").strip():
            raise ValueError("APPROVED_WITH_EDITS requires non-empty final_text")
        now = _now_iso()
        orig_hash = cur.get("orig_hash") or sha256_text(cur.get("draft_reply") or "")
        if to_status == "APPROVED_WITH_EDITS":
            final_hash = sha256_text(final_text or "")
        else:
            final_hash = orig_hash
        conn.execute(
            "UPDATE escalations SET status = ?, reviewer = ?, rationale = ?, final_text = ?,"
            " corrected_intent = ?, final_hash = ?, updated_at = ?, reviewed_at = ? WHERE id = ?",
            (
                to_status,
                reviewer or "reviewer",
                rationale or "",
                final_text if to_status == "APPROVED_WITH_EDITS" else cur.get("final_text"),
                corrected_intent,
                final_hash,
                now,
                now,
                escalation_id,
            ),
        )
        _append_audit(conn, escalation_id, to_status, reviewer or "reviewer",
                      rationale or "", orig_hash, final_hash, now)
        conn.commit()
        updated = conn.execute("SELECT * FROM escalations WHERE id = ?", (escalation_id,)).fetchone()
        return _row_to_dict(updated)
    finally:
        conn.close()


def expire_overdue(
    *,
    now_iso: str | None = None,
    db_path: str | Path | None = None,
    reviewer: str = "system",
) -> int:
    """Mark PENDING rows past sla_due_at as EXPIRED (with audit). Returns count."""
    init_db(db_path)
    now = now_iso or _now_iso()
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM escalations WHERE status = 'PENDING' AND sla_due_at IS NOT NULL"
            " AND sla_due_at < ?",
            (now,),
        ).fetchall()
        n = 0
        for r in rows:
            d = _row_to_dict(r)
            try:
                conn.execute(
                    "UPDATE escalations SET status='EXPIRED', reviewer=?, rationale=?,"
                    " final_hash=?, updated_at=?, reviewed_at=? WHERE id=? AND status='PENDING'",
                    (reviewer, "sla_expired",
                     d.get("orig_hash") or sha256_text(d.get("draft_reply") or ""),
                     now, now, d["id"]),
                )
                _append_audit(conn, d["id"], "EXPIRED", reviewer, "sla_expired",
                              d.get("orig_hash"), d.get("orig_hash"), now)
                n += 1
            except Exception:
                continue
        conn.commit()
        return n
    finally:
        conn.close()


def build_warm_transfer(row: dict) -> dict:
    """Handoff payload: transcript + intent/conf + reason + draft + next step + SLA."""
    reason = (row or {}).get("reason_code") or (row or {}).get("escalate_reason") or "unresolvable"
    draft = (row or {}).get("final_text") or (row or {}).get("draft_reply") or ""
    return {
        "escalation_id": (row or {}).get("id"),
        "brand": (row or {}).get("brand"),
        "transcript": (row or {}).get("text") or "",
        "intent": (row or {}).get("corrected_intent") or (row or {}).get("intent"),
        "intent_confidence": float((row or {}).get("intent_confidence") or 0.0),
        "reason_code": reason,
        "draft": draft,
        "grounding_passage_ids": (row or {}).get("grounding_passage_ids") or [],
        "next_step": _NEXT_STEP_BY_REASON.get(reason, _NEXT_STEP_BY_REASON["unresolvable"]),
        "sla_due_at": (row or {}).get("sla_due_at"),
        "status": (row or {}).get("status"),
        "created_at": (row or {}).get("created_at"),
    }


# ---- Autonomy matrix (intent x risk-tier x confidence-band -> route) ----

def load_matrix(matrix_path: str | Path | None = None) -> dict:
    """Load autonomy_matrix.yaml; fall back to built-in defaults if unavailable."""
    p = Path(matrix_path) if matrix_path else MATRIX_PATH
    defaults = {
        "version": 0,
        "risk_tiers": {
            "high": sorted(_FALLBACK_HIGH),
            "medium": sorted(_FALLBACK_MEDIUM),
            "low": [],
        },
        "confidence_bands": {"low_max": 0.45, "high_min": 0.7},
    }
    try:
        import yaml  # type: ignore
    except Exception:
        return defaults
    try:
        if not p.exists():
            return defaults
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            return defaults
        return data
    except Exception:
        return defaults


def risk_tier_for(intent: str, matrix: dict | None = None) -> str:
    m = matrix if isinstance(matrix, dict) else load_matrix()
    tiers = (m.get("risk_tiers") or {}) if isinstance(m, dict) else {}
    for tier in ("high", "medium"):
        try:
            if intent in list(tiers.get(tier) or []):
                return tier
        except Exception:
            continue
    return "low"


def confidence_band_for(conf: float, matrix: dict | None = None) -> str:
    m = matrix if isinstance(matrix, dict) else load_matrix()
    try:
        bands = (m.get("confidence_bands") or {}) if isinstance(m, dict) else {}
        if isinstance(bands, dict) and ("low" in bands or "high" in bands):
            low_max = float((bands.get("low") or {}).get("max", 0.45))
            high_min = float((bands.get("high") or {}).get("min", 0.7))
        else:
            low_max = float(bands.get("low_max", 0.45))
            high_min = float(bands.get("high_min", 0.7))
    except Exception:
        low_max, high_min = 0.45, 0.7
    try:
        c = float(conf)
    except Exception:
        c = 0.0
    if c < low_max:
        return "low"
    if c < high_min:
        return "medium"
    return "high"


def route_for(intent: str, confidence: float, matrix: dict | None = None) -> str:
    """Deterministic route: auto | review | must_review.

    Rules (v1, fail-closed):
      high risk            -> must_review (any confidence)
      medium + low conf    -> must_review
      medium + med/high    -> review
      low + high conf      -> auto
      low + low/med        -> review
    Explicit routing_rules in the YAML take precedence when present.
    """
    m = matrix if isinstance(matrix, dict) else load_matrix()
    tier = risk_tier_for(intent, m)
    band = confidence_band_for(confidence, m)
    try:
        rules = (m.get("routing_rules") or []) if isinstance(m, dict) else []
        for r in rules:
            if not isinstance(r, dict):
                continue
            if str(r.get("risk", "")) == tier and str(r.get("band", "")) == band:
                route = str(r.get("route", "review"))
                return route if route in ROUTES else "review"
    except Exception:
        pass
    if tier == "high":
        return "must_review"
    if tier == "medium":
        return "must_review" if band == "low" else "review"
    return "auto" if band == "high" else "review"


def stats(db_path: str | Path | None = None) -> dict:
    init_db(db_path)
    conn = _connect(db_path)
    try:
        by_status = {s: 0 for s in STATUSES}
        for r in conn.execute("SELECT status, COUNT(*) c FROM escalations GROUP BY status").fetchall():
            by_status[r[0]] = int(r[1])
        by_intent: dict = {}
        for r in conn.execute(
            "SELECT COALESCE(corrected_intent, intent) i, COUNT(*) c FROM escalations"
            " WHERE status IN ('APPROVED','APPROVED_WITH_EDITS') GROUP BY i"
        ).fetchall():
            by_intent[r[0]] = int(r[1])
        total = sum(by_status.values())
        return {"total": total, "by_status": by_status, "approved_by_intent": by_intent}
    finally:
        conn.close()
