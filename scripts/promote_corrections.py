"""Promote reviewer corrections to golden candidates (Phase 3).

Reads APPROVED_WITH_EDITS rows from data/processed/review_queue.db and appends
them to data/processed/golden_candidate.jsonl (dedupe on sha256 of text), with
per-intent correction counters in data/processed/correction_counts.json.

Retrain-trigger badge: any intent with >= 20 corrections flips
data/processed/retrain_trigger.json to {"triggered": true, ...} and prints a
badge line. Threshold constant RETRAIN_TRIGGER_N = 20.

Usage:
    python scripts/promote_corrections.py [--db PATH] [--out PATH] [--limit N]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import review_store as rs  # noqa: E402

RETRAIN_TRIGGER_N = 20
DEFAULT_OUT = ROOT / "data" / "processed" / "golden_candidate.jsonl"
DEFAULT_COUNTS = ROOT / "data" / "processed" / "correction_counts.json"
DEFAULT_BADGE = ROOT / "data" / "processed" / "retrain_trigger.json"


def _sha(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def _load_existing_hashes(out: Path) -> set:
    seen = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            try:
                obj = json.loads(line)
                t = obj.get("text") or ""
                if t:
                    seen.add(_sha(t))
            except Exception:
                continue
    return seen


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=None)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--counts", default=str(DEFAULT_COUNTS))
    ap.add_argument("--badge", default=str(DEFAULT_BADGE))
    ap.add_argument("--limit", type=int, default=10000)
    args = ap.parse_args()

    db_path = Path(args.db) if args.db else None
    out = Path(args.out)
    counts_p = Path(args.counts)
    badge_p = Path(args.badge)
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = rs.list_queue(status="APPROVED_WITH_EDITS", limit=args.limit, db_path=db_path)
    seen = _load_existing_hashes(out)
    counters: dict[str, int] = {}
    if counts_p.exists():
        try:
            counters = json.loads(counts_p.read_text(encoding="utf-8"))
        except Exception:
            counters = {}
    added = 0
    with out.open("a", encoding="utf-8") as f:
        for r in rows:
            text = (r.get("text") or "").strip()
            if not text or _sha(text) in seen:
                continue
            intent = r.get("corrected_intent") or r.get("intent") or "other_out_of_scope"
            cand = {
                "text": text,
                "human_intent": intent,
                "orig_intent": r.get("intent"),
                "corrected_draft": r.get("final_text") or "",
                "orig_draft": r.get("draft_reply") or "",
                "brand": r.get("brand"),
                "reason_code": r.get("reason_code"),
                "reviewer": r.get("reviewer"),
                "escalation_id": r.get("id"),
                "source": "hitl-review-queue",
            }
            f.write(json.dumps(cand, ensure_ascii=False) + "\n")
            seen.add(_sha(text))
            counters[intent] = int(counters.get(intent, 0)) + 1
            added += 1
    counts_p.write_text(json.dumps(counters, indent=2, sort_keys=True), encoding="utf-8")

    over = sorted([k for k, v in counters.items() if int(v) >= RETRAIN_TRIGGER_N])
    badge = {
        "triggered": bool(over),
        "threshold": RETRAIN_TRIGGER_N,
        "intents_over_threshold": over,
        "counters": counters,
    }
    badge_p.write_text(json.dumps(badge, indent=2, sort_keys=True), encoding="utf-8")

    print(f"promoted {added} corrections -> {out.name}; intents: {json.dumps(counters, sort_keys=True)}")
    if over:
        print(f"[RETRAIN-TRIGGER] >= {RETRAIN_TRIGGER_N}/intent: {', '.join(over)}")
    else:
        print(f"[no-trigger] no intent at >= {RETRAIN_TRIGGER_N} yet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
