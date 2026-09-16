"""Groq smoke: runs with/without key, prints draft_path per case.

- No key (default): every case must report draft_path=template (fail-closed).
- With GROQ_API_KEY/OPENAI_API_KEY set: reports groq vs template per case.
- Never prints secrets: only whether a key env var is set + which var.

Usage (from .):
    $env:PYTHONPATH="."
    python scripts\\groq_smoke.py            # no-key run
    $env:GROQ_API_KEY="gsk_..."; python scripts\\groq_smoke.py  # live run
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent import AppleAgent  # noqa: E402

CASES = [
    ("virgin", "my train from Euston was delayed 45 mins, how do I claim Delay Repay?"),
    ("virgin", "I was charged \u00a312 for my ticket, can I get a refund?"),
    ("virgin", "carriage overcrowded, we were stranded and need evacuation help"),
    ("virgin", "when is the next train to Birmingham?"),
    ("apple", "my iphone battery drains fast after ios 11 update"),
]


def _key_status():
    if os.environ.get("GROQ_API_KEY", "").strip():
        return "set (GROQ_API_KEY)"
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return "set (OPENAI_API_KEY fallback)"
    return "unset (template-only expected)"


def main() -> int:
    key_status = _key_status()
    no_key = key_status.startswith("unset")
    print(f"groq_smoke: key {key_status}")
    failures = []
    for brand, text in CASES:
        try:
            agent = AppleAgent(None, brand=brand)
            r = agent.handle(text)
            path = r.escalate_signals.get("draft_path", "?")
            greason = r.escalate_signals.get("groq_reason", "-")
            ok_len = len(r.draft_reply) <= 280
            print(
                f"[{brand}] {text[:56]!r} -> intent={r.intent} decision={r.decision} "
                f"draft_path={path} groq_reason={greason} len_ok={ok_len} | {r.draft_reply[:80]!r}"
            )
            if no_key and path != "template":
                failures.append((brand, text, path))
            if not ok_len:
                failures.append((brand, text, "too-long"))
        except Exception as e:  # smoke must surface crashes loudly
            print(f"[{brand}] {text[:56]!r} -> EXCEPTION {type(e).__name__}: {e}")
            failures.append((brand, text, f"exception:{type(e).__name__}"))
    if no_key:
        if failures:
            print(f"FAIL: no-key run must be all template, violations={failures}")
            return 1
        print(f"OK: no-key run, all {len(CASES)} cases draft_path=template.")
    else:
        print(f"OK: keyed run complete ({len(CASES)} cases, paths vary groq|template).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
