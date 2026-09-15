"""Build blinded 60-item second-annotator relabel pack (Workstream C1).

Samples 60 rows from evaluation/virgin/golden_human_200.csv stratified by
human_intent (6 per intent x 10 intents, seed 7 per repo convention), attaches
up to 2 prior thread turns as context (per evaluation/virgin/SAMPLING_NOTE.md:
"current tweet + up to 2 prior thread turns", resolved via
data/processed/virgin_threads.parquet), shuffles row order, and emits
evaluation/virgin/relabel_60_blind.csv with EMPTY label columns for the
human annotator to fill in a spreadsheet.

Zero label leakage: output carries NO weak/human labels, NO stratum tags, NO
review_type/note columns. The script grep-asserts this before exiting.

Usage:
    C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\make_relabel_pack.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "evaluation" / "virgin" / "golden_human_200.csv"
THREADS = ROOT / "data" / "processed" / "virgin_threads.parquet"
OUT = ROOT / "evaluation" / "virgin" / "relabel_60_blind.csv"

SEED = 7  # repo convention (see SAMPLING_NOTE.md)
PER_STRATUM = 6
LABEL_COLS = ["human_intent", "human_escalate", "human_reason"]

# Full label vocabulary that must never appear in the blind pack body.
INTENT_SLUGS = [
    "delay_claim", "ticket_change_refund", "timetable_platform", "lost_property",
    "complaint_service", "fare_ticketing", "accessibility_assistance",
    "howto_guidance", "support_access_followup", "other_out_of_scope",
]
REASON_SLUGS = [  # 'none' excluded: too common a word to grep-assert
    "legal_safety", "money_threshold", "money_review", "human_request",
    "unresolvable", "complaint_review",
]


def prior_context(threads: pd.DataFrame, text: str) -> tuple[str, str]:
    """Return (immediately-prior turn, second-prior turn) for a golden text.

    Matches the golden text to its thread row, orders the thread by
    (created_at, tweet_id), and takes up to 2 preceding turns. Returns
    ("", "") when the text is unmatched (e.g. singleton-orphan) or first
    in its thread.
    """
    hits = threads.index[threads["text"] == text].tolist()
    if not hits:
        return "", ""
    row = threads.loc[hits[0]]
    thr = threads[threads["thread_id"] == row["thread_id"]].sort_values(
        ["created_at", "tweet_id"], kind="mergesort"
    )
    pos = thr.index.get_loc(hits[0])
    if isinstance(pos, slice):  # duplicate index safety
        return "", ""
    priors = thr.iloc[max(0, pos - 2):pos]["text"].tolist()
    prior_1 = priors[-1] if len(priors) >= 1 else ""
    prior_2 = priors[-2] if len(priors) >= 2 else ""
    return prior_1, prior_2


def main() -> None:
    gold = pd.read_csv(GOLDEN)
    need = {"text", "human_intent"}
    if not need.issubset(gold.columns):
        raise SystemExit(f"MISSING columns in {GOLDEN}: {sorted(need - set(gold.columns))}")
    if gold["text"].duplicated().any():
        raise SystemExit("golden texts not unique: cannot join relabels back safely")

    strata = gold["human_intent"].value_counts()
    short = strata[strata < PER_STRATUM]
    if not short.empty:
        raise SystemExit(f"strata below take={PER_STRATUM}: {short.to_dict()}")
    if len(strata) != 10:
        raise SystemExit(f"expected 10 intent strata, found {len(strata)}: {sorted(strata.index)}")

    sample = gold.groupby("human_intent", group_keys=False)[gold.columns].apply(
        lambda g: g.sample(PER_STRATUM, random_state=SEED))
    sample = sample.sample(frac=1.0, random_state=SEED).reset_index(drop=True)  # blind order
    assert len(sample) == 60, len(sample)

    threads = pd.read_parquet(THREADS, columns=["thread_id", "tweet_id", "created_at", "text"])
    ctx = [prior_context(threads, t) for t in sample["text"].tolist()]

    pack = pd.DataFrame({
        "pack_id": [f"relabel_{i:02d}" for i in range(len(sample))],
        "text": sample["text"].tolist(),
        "context_prior_1": [c[0] for c in ctx],
        "context_prior_2": [c[1] for c in ctx],
        "human_intent": "",
        "human_escalate": "",
        "human_reason": "",
    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pack.to_csv(OUT, index=False)

    # ---- zero-leakage grep-asserts on the written file ----
    raw_lines = OUT.read_text(encoding="utf-8").splitlines()
    header = raw_lines[0].split(",")
    assert header == ["pack_id", "text", "context_prior_1", "context_prior_2"] + LABEL_COLS, header
    body = "\n".join(raw_lines[1:])
    for slug in INTENT_SLUGS + REASON_SLUGS:
        assert slug not in body, f"LEAKAGE: label value {slug!r} found in pack body"
    reread = pd.read_csv(OUT, keep_default_na=False)
    assert len(reread) == 60, len(reread)
    for c in LABEL_COLS:
        assert (reread[c].astype(str).str.strip() == "").all(), f"LEAKAGE: {c} not empty"
    leaked_cols = {"weak_intent", "review_type", "note", "source", "stratum"} & set(reread.columns)
    assert not leaked_cols, f"LEAKAGE columns: {leaked_cols}"

    n_ctx1 = int((pack["context_prior_1"] != "").sum())
    n_ctx2 = int((pack["context_prior_2"] != "").sum())
    print(f"wrote {len(pack)} rows -> {OUT}")
    print("strata sampled (human_intent x6, seed 7; row order shuffled, strata NOT in file):")
    for intent, n in sorted(sample["human_intent"].value_counts().items()):
        print(f"  {intent:28s} {n}")
    print(f"context coverage: prior_1 on {n_ctx1}/60, prior_2 on {n_ctx2}/60 "
          f"(empty = thread-start / singleton-orphan per SAMPLING_NOTE)")
    print("leakage asserts passed: no label columns/values in pack; label cells all empty")
    print()
    print("=" * 72)
    print("LABELING INSTRUCTIONS (annotator 2 — fill the 3 empty columns, one row each)")
    print("=" * 72)
    print("Rulebook: docs/ANNOTATION_PROTOCOL.md section 1 + intent DESCRIPTIONS in")
    print("  src/virgin_intents.py and money/safety lexicons cited there.")
    print("Columns to fill (leave NO blanks; save as CSV from your spreadsheet):")
    print("  human_intent   : one of delay_claim | ticket_change_refund |")
    print("                   timetable_platform | lost_property | complaint_service |")
    print("                   fare_ticketing | accessibility_assistance |")
    print("                   howto_guidance | support_access_followup |")
    print("                   other_out_of_scope")
    print("  human_escalate : 0 or 1 (1 = needs human review / cannot auto-handle)")
    print("  human_reason   : legal_safety | money_threshold | money_review |")
    print("                   human_request | unresolvable | complaint_review | none")
    print("Judge each row on text + context_prior_1/2 (prior thread turns, oldest last).")
    print("Do NOT look at golden_human_200.csv (that would unblind the study).")
    print("When done, run: .venv/Scripts/python scripts/compute_iaa.py")


if __name__ == "__main__":
    main()
