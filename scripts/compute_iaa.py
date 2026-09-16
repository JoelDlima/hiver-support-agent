"""Inter-annotator agreement for the golden-200 relabel study (Workstream C2).

Reads the filled blind pack (evaluation/virgin/relabel_60_blind.csv, produced
by scripts/make_relabel_pack.py and labelled by a human) plus the original
labels in evaluation/virgin/golden_human_200.csv (joined on exact text), and
computes Cohen's kappa overall + per-intent (one-vs-rest), raw agreement, and
top confusion pairs. Writes evaluation/virgin/GOLDEN_NOTE_APPENDIX_IAA.md.

Refuses with a clear error on empty/unfilled input. `--selftest` runs a
synthetic mode with hand-checkable tables that proves the math.

Usage:
    .venv\\Scripts\\python.exe scripts\\compute_iaa.py --selftest
    .venv\\Scripts\\python.exe scripts\\compute_iaa.py
"""

import argparse
import sys
import warnings
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score
from sklearn.exceptions import UndefinedMetricWarning

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "evaluation" / "virgin" / "relabel_60_blind.csv"
GOLDEN = ROOT / "evaluation" / "virgin" / "golden_human_200.csv"
OUT = ROOT / "evaluation" / "virgin" / "GOLDEN_NOTE_APPENDIX_IAA.md"

LABEL_COLS = ["human_intent", "human_escalate", "human_reason"]
INTENT_VOCAB = [
    "delay_claim", "ticket_change_refund", "timetable_platform", "lost_property",
    "complaint_service", "fare_ticketing", "accessibility_assistance",
    "howto_guidance", "support_access_followup", "other_out_of_scope",
]
REASON_VOCAB = [
    "legal_safety", "money_threshold", "money_review", "human_request",
    "unresolvable", "complaint_review", "none",
]


def _norm_esc(v) -> int:
    s = str(v).strip().lower()
    if s in ("1", "1.0", "true", "yes"):
        return 1
    if s in ("0", "0.0", "false", "no"):
        return 0
    raise ValueError(f"bad human_escalate value {v!r} (want 0/1)")


def filled_rows(pack: pd.DataFrame) -> pd.DataFrame:
    """Rows where the annotator filled all three label columns."""
    mask = pd.Series(True, index=pack.index)
    for c in LABEL_COLS:
        if c not in pack.columns:
            return pack.iloc[0:0]
        mask &= pack[c].notna() & (pack[c].astype(str).str.strip() != "")
    return pack[mask]


def compute_metrics(a1_intent, a2_intent, a1_esc, a2_esc) -> dict:
    """Core math (pure function — also exercised by --selftest)."""
    n = len(a1_intent)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UndefinedMetricWarning)
        warnings.simplefilter("ignore", UserWarning)
        intent_kappa = float(cohen_kappa_score(a1_intent, a2_intent))
        esc_kappa = float(cohen_kappa_score(a1_esc, a2_esc))
        intent_agree = float(sum(a == b for a, b in zip(a1_intent, a2_intent)) / n)
        esc_agree = float(sum(a == b for a, b in zip(a1_esc, a2_esc)) / n)
        per_intent = {}
        for intent in sorted(set(a1_intent) | set(a2_intent)):
            b1 = [1 if x == intent else 0 for x in a1_intent]
            b2 = [1 if x == intent else 0 for x in a2_intent]
            try:
                k = float(cohen_kappa_score(b1, b2))
            except Exception:
                k = float("nan")
            per_intent[intent] = {
                "kappa": k,
                "agree": float(sum(a == b for a, b in zip(b1, b2)) / n),
                "n1": int(sum(b1)),
                "n2": int(sum(b2)),
            }
        conf = (
            pd.DataFrame({"a1": a1_intent, "a2": a2_intent})
            .groupby(["a1", "a2"]).size().reset_index(name="n")
            .query("a1 != a2").sort_values("n", ascending=False)
        )
    return {
        "n": n,
        "intent_kappa": intent_kappa,
        "esc_kappa": esc_kappa,
        "intent_agree": intent_agree,
        "esc_agree": esc_agree,
        "per_intent": per_intent,
        "confusion": conf,
    }


def write_appendix(m: dict) -> None:
    gate = 0.60
    verdict = ("PASS" if m["intent_kappa"] >= gate and m["esc_kappa"] >= gate else "FAIL")
    lines = [
        "# GOLDEN-200 Appendix: second-annotator agreement (IAA, n=60)",
        "",
        f"Second-annotator blind relabel of a stratified 60-item slice of",
        f"`golden_human_200.csv` (6 per intent x 10 intents, seed 7; pack built by",
        f"`scripts/make_relabel_pack.py`, labels joined on exact text).",
        f"Computed by `scripts/compute_iaa.py`.",
        "",
        "## Headline",
        "",
        "| metric | value |",
        "|---|---|",
        f"| n (double-labelled) | {m['n']} |",
        f"| intent Cohen k | {m['intent_kappa']:.3f} |",
        f"| intent raw agreement | {m['intent_agree']:.3f} |",
        f"| escalate Cohen k | {m['esc_kappa']:.3f} |",
        f"| escalate raw agreement | {m['esc_agree']:.3f} |",
        f"| ship gate (intent k >= 0.60 AND esc k >= 0.60) | **{verdict}** |",
        "",
        "## Per-intent kappa (one-vs-rest)",
        "",
        "| intent | k | raw agree | n (ann1) | n (ann2) |",
        "|---|---|---|---|---|",
    ]
    for intent, d in sorted(m["per_intent"].items()):
        lines.append(f"| {intent} | {d['kappa']:.3f} | {d['agree']:.3f} | {d['n1']} | {d['n2']} |")
    lines += [
        "",
        "## Top confusion pairs (annotator-1 -> annotator-2)",
        "",
        "| ann1 | ann2 | n |",
        "|---|---|---|",
    ]
    for _, r in m["confusion"].head(8).iterrows():
        lines.append(f"| {r['a1']} | {r['a2']} | {int(r['n'])} |")
    if m["confusion"].empty:
        lines.append("| (none — perfect intent agreement) | | |")
    lines += [
        "",
        "## Caveats (n=60)",
        "",
        "- n=60 (~6 per intent) bounds precision: per-intent kappas carry wide",
        "  confidence intervals; treat single-intent k < 0.60 as a flag for rulebook",
        "  review (per docs/ANNOTATION_PROTOCOL.md section 1), not a verdict.",
        "- The blind pack carries prior-turn context (up to 2 thread turns); residual",
        "  disagreement on follow-ups (`Yes`/`Both`/thanks-acks) is expected and",
        "  adjudicated by the rulebook, not by re-sampling.",
        "- Weak (keyword) labels are excluded from this study by design — headline",
        "  metrics use human labels only.",
        "",
        "## Impact statement",
        "",
        f"The golden-200 was single-annotated; this study bounds that limitation at",
        f"intent k={m['intent_kappa']:.2f} / escalate k={m['esc_kappa']:.2f} (n={m['n']}).",
        ("Agreement clears the 0.60 ship gate: single-annotator labels stand with a "
         "measured reliability bound."
         if verdict == "PASS" else
         "Agreement misses the 0.60 ship gate: per protocol, revise the rulebook "
         "(src/virgin_intents.py DESCRIPTIONS + money/safety lexicons) and re-adjudicate "
         "disagreements — do not tune metrics to the test set."),
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


def selftest() -> None:
    """Synthetic mode: hand-checkable tables proving the kappa math."""
    # T1: perfect agreement -> k = 1, agree = 1.
    a = ["x", "y", "x", "y", "z", "z"]
    m = compute_metrics(a, list(a), [0, 1, 0, 1, 0, 1], [0, 1, 0, 1, 0, 1])
    assert m["intent_kappa"] == 1.0, m["intent_kappa"]
    assert m["esc_kappa"] == 1.0, m["esc_kappa"]
    assert m["intent_agree"] == 1.0 and m["esc_agree"] == 1.0
    print("selftest T1 perfect-agreement (k=1.0): PASS")

    # T2: 2x2 table [[30 agree-0, 10 A1-only], [10 A2-only, 50 agree-1]] (n=100).
    # po = .8, pe = .4*.4 + .6*.6 = .52 -> k = .28/.48 = 0.58333.
    b1 = [0] * 40 + [1] * 60
    b2 = [0] * 30 + [1] * 10 + [0] * 10 + [1] * 50
    m2 = compute_metrics(
        ["i"] * 100, ["i"] * 100, b1, b2)
    assert abs(m2["esc_kappa"] - 0.583333) < 1e-6, m2["esc_kappa"]
    assert abs(m2["esc_agree"] - 0.80) < 1e-9, m2["esc_agree"]
    print(f"selftest T2 hand-kappa 0.583333 (got {m2['esc_kappa']:.6f}): PASS")

    # T3: confusion pairs surface the top disagreement.
    c1 = ["delay_claim"] * 8 + ["complaint_service"] * 4
    c2 = ["delay_claim"] * 8 + ["ticket_change_refund"] * 4
    m3 = compute_metrics(c1, c2, [0] * 12, [0] * 12)
    top = m3["confusion"].iloc[0]
    assert (top["a1"], top["a2"], int(top["n"])) == (
        "complaint_service", "ticket_change_refund", 4), top.to_dict()
    assert abs(m3["intent_agree"] - 8 / 12) < 1e-9
    print("selftest T3 top-confusion-pair extraction: PASS")

    # T4: per-intent one-vs-rest kappa on a known split.
    d1 = ["x"] * 6 + ["y"] * 6
    d2 = ["x"] * 5 + ["y"] + ["y"] * 6  # one x->y flip
    m4 = compute_metrics(d1, d2, [0] * 12, [0] * 12)
    assert set(m4["per_intent"]) == {"x", "y"}
    assert m4["per_intent"]["x"]["n1"] == 6 and m4["per_intent"]["x"]["n2"] == 5
    print(f"selftest T4 per-intent kappa (x k={m4['per_intent']['x']['kappa']:.4f}): PASS")
    print("selftest: ALL 4 GREEN")


def main() -> None:
    global OUT
    ap = argparse.ArgumentParser(description="IAA kappa for the golden-200 relabel study")
    ap.add_argument("--selftest", action="store_true", help="synthetic math check, no files read/written")
    ap.add_argument("--pack", default=str(PACK))
    ap.add_argument("--golden", default=str(GOLDEN))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return

    OUT = Path(args.out)
    pack_path, gold_path = Path(args.pack), Path(args.golden)
    if not pack_path.exists():
        sys.exit(f"ERROR: pack not found: {pack_path}\n"
                 f"Build it first: .venv/Scripts/python scripts/make_relabel_pack.py")
    pack = pd.read_csv(pack_path, keep_default_na=False)
    done = filled_rows(pack)
    if len(done) == 0:
        sys.exit(
            f"ERROR: no filled labels in {pack_path} "
            f"({len(pack)} rows, 0 with human_intent/escalate/reason all filled).\n"
            "The pack is still blank — open it in a spreadsheet, fill human_intent / "
            "human_escalate / human_reason per docs/ANNOTATION_PROTOCOL.md §1, save, re-run.\n"
            "Sanity math only (no input needed): "
            ".venv/Scripts/python scripts/compute_iaa.py --selftest")
    if len(done) < len(pack):
        print(f"note: {len(pack) - len(done)}/{len(pack)} rows still blank — scoring {len(done)} filled rows")

    # Validate vocab before scoring.
    bad_int = sorted(set(done["human_intent"].astype(str).str.strip()) - set(INTENT_VOCAB))
    if bad_int:
        sys.exit(f"ERROR: unknown human_intent values {bad_int} (want one of {INTENT_VOCAB})")
    bad_re = sorted(set(done["human_reason"].astype(str).str.strip()) - set(REASON_VOCAB))
    if bad_re:
        sys.exit(f"ERROR: unknown human_reason values {bad_re} (want one of {REASON_VOCAB})")
    try:
        esc2 = [_norm_esc(v) for v in done["human_escalate"].tolist()]
    except ValueError as e:
        sys.exit(f"ERROR: {e}")

    gold = pd.read_csv(gold_path)
    orig = dict(zip(gold["text"].tolist(),
                     zip(gold["human_intent"].tolist(),
                         gold["human_escalate"].astype(int).tolist())))
    missing = [t for t in done["text"].tolist() if t not in orig]
    if missing:
        sys.exit(f"ERROR: {len(missing)} pack texts not found in {gold_path} "
                 f"(pack edited? first 40 chars: {missing[0][:40]!r})")

    a1 = [orig[t] for t in done["text"].tolist()]
    m = compute_metrics(
        [x[0] for x in a1],
        done["human_intent"].astype(str).str.strip().tolist(),
        [x[1] for x in a1],
        esc2,
    )
    print(f"n={m['n']} intent k={m['intent_kappa']:.3f} agree={m['intent_agree']:.3f} | "
          f"esc k={m['esc_kappa']:.3f} agree={m['esc_agree']:.3f}")
    write_appendix(m)


if __name__ == "__main__":
    main()
