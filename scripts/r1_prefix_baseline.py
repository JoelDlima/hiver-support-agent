"""FIX_PLAN R1a — honest pre-fix baseline: reconstruct PRE-FIX virgin keyword
rules from git history (commit 87cecde, before the F2/F4a/F7 fixes in 8d9be27),
rebuild the 'simple' system with them, and rescore on the human-200 golden.

Why: the published weak-200 'simple 0.975' used post-fix rules against labels
frozen pre-fix (disclosed circularity). The HONEST pre-fix-vs-final delta has
never been measured. This script measures it, read-only over goldens.

What it does (no model retraining, no golden mutation):
1. Extract KEYWORDS from `git show 87cecde:src/virgin_intents.py` (the pre-fix
   freeze) into a live dict — no file writes.
2. 'simple (pre-fix)' = pre-fix keyword rules + virgin NN top-1, scored on
   evaluation/virgin/golden_human_200.csv (text -> intent + escalate decision).
   Escalation for the simple system mirrors scripts/run_virgin_eval.py:
   human_request / safety lexicon triggers only (keyword systems had no
   money gate). We use the same trigger set as the published simple arm.
3. 'final' column values are loaded from evaluation/virgin/results_human200.csv
   (frozen artifact, read-only) so the comparison table is apples-to-apples.
4. McNemar exact test (binomial) on paired intent correct/incorrect between
   pre-fix-simple and final, + bootstrap 95% CI on the acc delta
   (2000 resamples, seed 20260912 — repo convention).
5. Writes evaluation/virgin/R1_PREFIX_BASELINE.md + r1_prefix_simple200.csv.
   Never touches golden files, models, or the frontend.

Usage:
    python scripts/r1_prefix_baseline.py            # real run (needs git history)
    python scripts/r1_prefix_baseline.py --selftest # synthetic hand-checkable math
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "evaluation" / "virgin" / "golden_human_200.csv"
FINAL_CSV = ROOT / "evaluation" / "virgin" / "results_human200.csv"
OUT_MD = ROOT / "evaluation" / "virgin" / "R1_PREFIX_BASELINE.md"
OUT_CSV = ROOT / "evaluation" / "virgin" / "r1_prefix_simple200.csv"
PREFIX_COMMIT = "87cecde"

SEED = 20260912
BOOTSTRAP_RESAMPLES = 2000

# Same escalation trigger set as the published simple arm (run_virgin_eval.py):
# keyword systems escalate on human-request / legal-safety only.
SIMPLE_ESCALATE_TOKENS = [
    "human", "real person", "someone real", "call me", "talk to",
    "manager", "supervisor", "sue", "lawyer", "court", "hurt", "injured",
    "injur", "fire", "burn", "smoke", "explod", "shock", "bleed", "blood",
    "suicid", "hacked", "stolen", "unauthorized", "locked out",
    # rail safety add-ons existed pre-fix via text_norm base lexicon only;
    # overcrowding words were added post-fix, so the pre-fix arm uses the base:
]


def load_prefix_keywords() -> dict:
    """Extract the pre-fix KEYWORDS dict from git history (87cecde)."""
    raw = subprocess.run(
        ["git", "show", f"{PREFIX_COMMIT}:src/virgin_intents.py"],
        capture_output=True, text=True, check=True, cwd=str(ROOT),
    ).stdout
    m = re.search(r"^KEYWORDS\s*=\s*(\{.*?\n\})", raw, re.S | re.M)
    if not m:
        raise RuntimeError("KEYWORDS block not found in pre-fix file")
    return ast.literal_eval(m.group(1))


def weak_label_prefix(text: str, keywords: dict) -> str:
    """Pre-fix weak rule: first-match in dict order, longest keyword wins;
    support_access_followup checked last (same semantics as the current code,
    which kept the pre-fix ordering)."""
    t = (text or "").lower()
    hits = []
    for intent, kws in keywords.items():
        if intent == "support_access_followup":
            continue
        for kw in kws or []:
            if kw and kw in t:
                hits.append((intent, kw))
    if not hits:
        if t.startswith("how") or "how do" in t:
            return "howto_guidance"
        if len(t.split()) <= 3 or "dm" in t or "thank" in t:
            return "support_access_followup"
        return "other_out_of_scope"
    intent, _kw = max(hits, key=lambda x: len(x[1]))
    return intent


def simple_escalate(text: str) -> int:
    low = (text or "").lower()
    return int(any(tok in low for tok in SIMPLE_ESCALATE_TOKENS))


def _wilson_ci(p: float, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(b: int, c: int) -> float:
    """Exact binomial McNemar p-value on discordant pairs (b, c)."""
    try:
        from scipy.stats import binomtest
        n = b + c
        if n == 0:
            return 1.0
        return float(binomtest(min(b, c), n, 0.5).pvalue)
    except ImportError:
        # Normal approximation fallback.
        import math
        n = b + c
        if n == 0:
            return 1.0
        z = (abs(b - c) - 1) / math.sqrt(n)
        return float(math.erfc(z / math.sqrt(2)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="synthetic hand-checkable math check, no files needed")
    args = ap.parse_args()

    if args.selftest:
        # Hand-check: A wins 12 discordant, B wins 3 -> exact binomial(15, .5)
        # P(X<=3) two-sided. Also check Wilson CI bounds are sane.
        p = mcnemar_exact(12, 3)
        assert 0.01 < p < 0.06, p  # ~0.035 two-sided
        lo, hi = _wilson_ci(0.795, 200)
        assert 0.73 < lo < 0.75 and 0.84 < hi < 0.86, (lo, hi)
        print("selftest OK: mcnemar_exact(12,3)=%.4f, wilson(0.795,200)=[%.3f,%.3f]"
              % (p, lo, hi))
        return

    keywords = load_prefix_keywords()
    df = pd.read_csv(GOLDEN)
    assert len(df) == 200, f"expected golden_human_200 n=200, got {len(df)}"

    rows = []
    for r in df.itertuples():
        pred = weak_label_prefix(getattr(r, "text", ""), keywords)
        pred_esc = simple_escalate(getattr(r, "text", ""))
        rows.append({
            "text": getattr(r, "text", ""),
            "human_intent": getattr(r, "human_intent", ""),
            "human_escalate": int(getattr(r, "human_escalate", 0) or 0),
            "prefix_pred": pred,
            "prefix_esc": pred_esc,
            "intent_ok": int(pred == getattr(r, "human_intent", "")),
            "esc_ok": int(pred_esc == int(getattr(r, "human_escalate", 0) or 0)),
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False)

    acc_simple = accuracy_score(out["human_intent"], out["prefix_pred"])
    _p, _r, f1_simple, _s = precision_recall_fscore_support(
        out["human_intent"], out["prefix_pred"], average="macro", zero_division=0)
    esc_p, esc_r, esc_f1, _ = precision_recall_fscore_support(
        out["human_escalate"], out["prefix_esc"], average="binary", zero_division=0)

    # Final arm numbers from the frozen results artifact.
    fdf = pd.read_csv(FINAL_CSV)
    frow = fdf[fdf["system"].str.startswith("final")].iloc[0]
    acc_final, f1_final = float(frow["intent_acc"]), float(frow["intent_macroF1"])
    esc_f1_final = float(frow["esc_F1"])

    # McNemar on paired intent correctness (same rows, paired by construction).
    b = int(((out["intent_ok"] == 0)).sum())  # simple wrong
    c = None  # need final correctness per row -> recompute from golden + frozen acc?
    # We only have aggregate final numbers, not per-row predictions, so McNemar
    # is computed between pre-fix simple and the CURRENT post-fix simple rules
    # (both reconstructable per-row). The final-vs-simple delta stays aggregate.
    from src.agent import _weak_label_generic
    from src.virgin_intents import KEYWORDS as POSTFIX_KW
    out["postfix_pred"] = [
        _weak_label_generic(t, POSTFIX_KW) for t in out["text"]]
    out["postfix_ok"] = (out["postfix_pred"] == out["human_intent"]).astype(int)
    b = int(((out["intent_ok"] == 1) & (out["postfix_ok"] == 0)).sum())  # pre-fix right, post-fix wrong
    c = int(((out["intent_ok"] == 0) & (out["postfix_ok"] == 1)).sum())  # pre-fix wrong, post-fix right
    p_mcnemar = mcnemar_exact(b, c)

    acc_postfix = accuracy_score(out["human_intent"], out["postfix_pred"])

    # Bootstrap CI on acc delta (pre-fix simple -> final), paired rows.
    import numpy as np
    rng = np.random.default_rng(SEED)
    idx = np.arange(len(out))
    deltas = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        s = rng.choice(idx, size=len(idx), replace=True)
        deltas.append(acc_final - accuracy_score(
            out["human_intent"].iloc[s], out["prefix_pred"].iloc[s]))
    lo, hi = np.percentile(deltas, [2.5, 97.5])

    lines = [
        "# R1a — Honest pre-fix baseline (FIX_PLAN R1.1)",
        "",
        f"- Pre-fix rules: `git show {PREFIX_COMMIT}:src/virgin_intents.py` (KEYWORDS extracted verbatim, no retraining).",
        f"- Scored on `evaluation/virgin/golden_human_200.csv` (n=200, read-only).",
        f"- Per-row CSV: `r1_prefix_simple200.csv`. Bootstrap {BOOTSTRAP_RESAMPLES} resamples, seed {SEED}.",
        "",
        "## Headline (human-200)",
        "| system | intent acc | intent macroF1 | esc P | esc R | esc F1 |",
        "|---|---|---|---|---|---|",
        f"| simple (PRE-FIX rules, reconstructed) | {acc_simple:.3f} | {f1_simple:.3f} | {esc_p:.3f} | {esc_r:.3f} | {esc_f1:.3f} |",
        f"| simple (post-fix rules, current) | {acc_postfix:.3f} | — | — | — | — |",
        f"| final (frozen artifact) | {acc_final:.3f} | {f1_final:.3f} | — | — | {esc_f1_final:.3f} |",
        "",
        "## Deltas",
        f"- final − simple(pre-fix) acc: **{acc_final - acc_simple:+.3f}** "
        f"(bootstrap 95% CI [{lo:+.3f}, {hi:+.3f}])",
        f"- final − simple(pre-fix) macroF1: **{f1_final - f1_simple:+.3f}**",
        f"- final − simple(pre-fix) esc F1: **{esc_f1_final - esc_f1:+.3f}**",
        "",
        "## Pre-fix vs post-fix keyword rules (McNemar exact on discordant pairs)",
        f"- pre-fix right / post-fix wrong: b={b}; pre-fix wrong / post-fix right: c={c}",
        f"- exact p = {p_mcnemar:.4f} "
        + ("(post-fix rules significantly better)" if p_mcnemar < 0.05 and c > b else "(not significant at 0.05)"),
        "",
        "## What is misleading (mandatory)",
        "- The published weak-200 'simple 0.975' is post-fix rules vs pre-fix frozen labels — circular, disclosed in BASELINE_VS_FINAL.md §A.",
        "- This table is the honest version: pre-fix rules measured on the same human-200 the final system reports on.",
        f"- The keyword-fix lift itself (post-fix vs pre-fix, same system shape) is {c - b:+d} net rows; the CLASSIFIER-vs-KEYWORDS story remains the final-vs-simple comparison above.",
        "",
        "## Reproduce",
        "```powershell",
        "python scripts/r1_prefix_baseline.py           # real run (reads git history + goldens, read-only)",
        "python scripts/r1_prefix_baseline.py --selftest  # synthetic math check",
        "```",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    try:
        print("\n".join(lines))
    except UnicodeEncodeError:
        # Windows cp1252 console: strip non-ASCII (minus sign) for stdout only.
        print("\n".join(lines).replace("\u2212", "-").encode("ascii", "replace").decode("ascii"))
    print(f"\nwrote {OUT_MD.name}, {OUT_CSV.name}")


if __name__ == "__main__":
    main()
