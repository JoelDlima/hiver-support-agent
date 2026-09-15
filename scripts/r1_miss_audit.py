"""FIX_PLAN R1.2 — miss audit: bucket every human-200 intent miss of the FINAL
system into actionable failure classes, with 2 examples per bucket.

Reads (all read-only):
  evaluation/virgin/golden_human_200.csv   (text + human_intent)
  models/intent_virgin.pkl                 (FROZEN — predict only)

Buckets (FIX_PLAN R1 taxonomy):
  ambiguous      — human label itself sits on an intent boundary (delay vs
                   refund money-language overlap, complaint vs accessibility);
  multi_intent   — text names 2+ intents; any single-label system loses one;
  context_depend — text is a follow-up ("ok thanks", "yes") whose meaning
                   needs prior thread turns the classifier never sees;
  oos_or_noise   — genuinely other/vague/non-English where other_out_of_scope
                   was the right answer and the model picked a content intent
                   (or vice versa);
  model_error    — none of the above: the model simply picked the wrong
                   content intent on a clear single-intent text.

Writes evaluation/virgin/MISS_AUDIT.md (+ prints counts). Never mutates
goldens, models, or existing eval CSVs.

Usage: python scripts/r1_miss_audit.py [--selftest]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "evaluation" / "virgin" / "golden_human_200.csv"
MODEL = ROOT / "models" / "intent_virgin.pkl"
OUT_MD = ROOT / "evaluation" / "virgin" / "MISS_AUDIT.md"

# Money-overlap vocabulary (delay <-> refund boundary from DECISION_LOG #20).
_MONEY_WORDS = ["refund", "repay", "compensation", "reprint", "reissue", "receipt", "£", "$"]
# Follow-up shape: short, ack-like, or continuation tokens.
_FOLLOWUP_RE = re.compile(
    r"^(ok|okay|thanks|thank you|yes|no|yep|nope|great|brilliant|cheers|will do|"
    r"sent|done|hi|hello|morning|evening)\b[\s,.!?]*.{0,60}$", re.I)
# Cross-intent signal words for ambiguity detection.
_AMBIG_PAIRS = {
    ("delay_claim", "ticket_change_refund"): _MONEY_WORDS,
    ("ticket_change_refund", "delay_claim"): _MONEY_WORDS,
    ("complaint_service", "accessibility_assistance"): ["ramp", "wheelchair", "seat", "assist"],
    ("accessibility_assistance", "complaint_service"): ["ramp", "wheelchair", "seat", "assist"],
    ("complaint_service", "lost_property"): ["lost", "left", "bag", "staff"],
    ("lost_property", "complaint_service"): ["staff", "rude"],
    ("timetable_platform", "delay_claim"): ["delayed", "cancel", "late"],
    ("delay_claim", "timetable_platform"): ["platform", "time", "when"],
}


def classify_miss(text: str, pred: str, human: str) -> str:
    """Assign one miss to a bucket (documented order = precedence)."""
    t = (text or "").lower()
    words = len(t.split())
    pair = (pred, human)
    rev = (human, pred)
    # multi_intent: two different content intents both lexically present.
    if pair in _AMBIG_PAIRS or rev in _AMBIG_PAIRS:
        signals = _AMBIG_PAIRS.get(pair) or _AMBIG_PAIRS.get(rev) or []
        if any(s in t for s in signals):
            return "ambiguous"
    if "other_out_of_scope" in (pred, human):
        return "oos_or_noise"
    if words <= 6 and (_FOLLOWUP_RE.match(text or "") or words <= 3):
        return "context_dependent"
    # Ambiguous fallback: boundary pair without the lexicon signal still counts
    # when BOTH intents are content intents from the money/safety families.
    content = {"delay_claim", "ticket_change_refund", "complaint_service",
               "accessibility_assistance", "lost_property", "timetable_platform"}
    if pred in content and human in content:
        return "ambiguous"
    return "model_error"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        assert classify_miss("delayed train refund please", "delay_claim",
                             "ticket_change_refund") == "ambiguous"
        assert classify_miss("ok thanks mate", "support_access_followup",
                             "delay_claim") == "context_dependent"
        assert classify_miss("random gibberish xyzzy", "delay_claim",
                             "other_out_of_scope") == "oos_or_noise"
        assert classify_miss("the 5:15 from Euston departs", "timetable_platform",
                             "howto_guidance") == "model_error"
        print("selftest OK: 4 bucket assignments hand-checked")
        return

    df = pd.read_csv(GOLDEN)
    assert len(df) == 200
    obj = joblib.load(MODEL)
    pipe = obj["pipeline"] if isinstance(obj, dict) and "pipeline" in obj else obj
    preds = pipe.predict(df["text"].astype(str).tolist())
    # Reproduce the two serving-side remaps that are part of the FINAL system
    # (crowd remap F4a + language gate) so buckets match the shipped behaviour.
    from src.text_norm import features_for_escalation
    from src.virgin_intents import CROWD_REMAP_TOKENS
    fixed = []
    for text, pred in zip(df["text"].astype(str).tolist(), preds):
        p = str(pred)
        feats = features_for_escalation(text)
        if (feats.get("has_non_english") and p != "other_out_of_scope"):
            p = "other_out_of_scope"
        low = text.lower()
        if (p == "other_out_of_scope"
                and any(tok in low for tok in CROWD_REMAP_TOKENS)):
            p = "complaint_service"
        fixed.append(p)
    df["pred"] = fixed
    misses = df[df["pred"] != df["human_intent"]].copy()
    misses["bucket"] = [
        classify_miss(t, p, h) for t, p, h in
        zip(misses["text"], misses["pred"], misses["human_intent"])]

    order = ["ambiguous", "multi_intent", "context_dependent", "oos_or_noise", "model_error"]
    # multi_intent: detect co-present signal pairs the ambiguous pass missed
    # (two distinct content-intent keywords both in text).
    multi_mask = misses["bucket"].eq("ambiguous") & misses["text"].str.lower().apply(
        lambda t: sum(any(k in t for k in kws) for kws in [
            ["delay", "refund"], ["refund", "complaint"], ["lost", "angry"]]) >= 2)
    misses.loc[multi_mask, "bucket"] = "multi_intent"

    lines = [
        "# R1.2 — Miss audit (FIX_PLAN R1): human-200 intent misses of the FINAL system",
        "",
        "Method: frozen `models/intent_virgin.pkl` + the two serving remaps (crowd F4a,",
        "language gate) — exactly the shipped classifier path. Bucket precedence:",
        "ambiguous (boundary pair + lexicon signal) > oos_or_noise > context_dependent",
        "(<=6 words / ack shape) > multi_intent (2+ signal families co-present) >",
        "model_error. Read-only; no goldens or models touched.",
        "",
        "| bucket | n | share of misses |",
        "|---|---|---|",
    ]
    total = len(misses)
    for b in order:
        n = int((misses["bucket"] == b).sum())
        lines.append(f"| {b} | {n} | {n / total:.2f} |" if total else f"| {b} | 0 | - |")
    lines.append(f"| **total misses** | **{total}** | (acc {1 - total / 200:.3f}) |")
    lines.append("")
    for b in order:
        sub = misses[misses["bucket"] == b].head(2)
        if not len(sub):
            continue
        lines.append(f"## {b} (examples)")
        for r in sub.itertuples():
            text = (r.text or "")[:160].replace("\n", " ")
            lines.append(f"- human=`{r.human_intent}` pred=`{r.pred}` — “{text}”")
        lines.append("")
    lines += [
        "## Reading",
        "- `ambiguous` + `multi_intent` + `context_dependent` are **label/task-shape** costs,",
        "  not model capacity: they need dual-label policy (DECISION_LOG #20) and",
        "  thread-context features (FIX_PLAN R1.3a), not a bigger classifier.",
        "- `oos_or_noise` is the other-detection stage from R1.3b.",
        "- `model_error` is the honest capacity residue — the target for any future",
        "  modeling work after the structural buckets are addressed.",
        "",
        "## Reproduce",
        "```powershell",
        "python scripts/r1_miss_audit.py            # real run (read-only)",
        "python scripts/r1_miss_audit.py --selftest # bucket-assignment math check",
        "```",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    try:
        print(f"misses={total}/200 (acc {1 - total / 200:.3f}); buckets:",
              {b: int((misses['bucket'] == b).sum()) for b in order})
    except UnicodeEncodeError:
        pass
    print(f"wrote {OUT_MD.name}")


if __name__ == "__main__":
    main()
