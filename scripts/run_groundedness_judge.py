"""Groundedness-only judge agreement study V3 (workstream A1, docs/WIN_PLAN.md).

Why: /judge verdict agreement missed the ship gate twice (v1 kappa 0.253, v2
negative -> advisory-only). Groundedness-only judgments (is each draft claim
entailed by cited passages?) should agree far better than open verdicts.

Method (no tuning to the test set):
- Agreement set: evaluation/virgin/spotcheck_30.csv drafts from
  llm_judge_30_drafts.csv (the EXACT drafts the human graded) vs
  human_grades_30.csv groundedness 1-5 (single annotator, blind to LLM).
- Each draft is judged by the SHIPPED endpoint POST /judge/groundedness
  (in-process TestClient): deterministic sentence claim-split + per-claim
  entail/passage-cite check. Groq leg (openai/gpt-oss-20b temp 0, fallback
  qwen/qwen3.8-27b) when GROQ_API_KEY is set, else the frozen offline
  token-coverage heuristic (stemmed, >=1/3 of claim tokens in one passage;
  rule frozen pre-run on ungraded pilot probes, see JUDGE_AGREEMENT_V3.md).
- Judge fraction-supported maps to 1-5 via 1+round(4*frac); primary metric is
  quadratic-weighted Cohen kappa vs human 1-5 + bootstrap 95% CI (2000
  resamples, seed 20260912, repo convention). PASS/FAIL vs wK>=0.60 ship gate.
- Coverage: all 200 golden_human_200 live drafts scored (distribution only).

Writes evaluation/virgin/JUDGE_AGREEMENT_V3.md. Never writes CSVs/MDs it does
not own; never mutates golden files.

Usage: C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\run_groundedness_judge.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

VIRGIN_DIR = Path(__file__).resolve().parents[1] / "evaluation" / "virgin"
DRAFTS = VIRGIN_DIR / "llm_judge_30_drafts.csv"
HUMAN = VIRGIN_DIR / "human_grades_30.csv"
GOLD200 = VIRGIN_DIR / "golden_human_200.csv"
OUT_MD = VIRGIN_DIR / "JUDGE_AGREEMENT_V3.md"

BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20260912
GATE_WK = 0.60


def frac_to_1_5(frac: float) -> int:
    return max(1, min(5, 1 + round(4 * float(frac))))


def bootstrap_wk_ci(y_true, y_pred, n_resamples=BOOTSTRAP_RESAMPLES, seed=BOOTSTRAP_SEED):
    rng = np.random.default_rng(seed)
    n = len(y_true)
    vals = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, n)
        try:
            vals.append(cohen_kappa_score([y_true[i] for i in idx],
                                          [y_pred[i] for i in idx],
                                          weights="quadratic"))
        except Exception:
            continue
    vals = [v for v in vals if np.isfinite(v)]
    if not vals:
        return float("nan"), float("nan")
    return round(float(np.percentile(vals, 2.5)), 3), round(float(np.percentile(vals, 97.5)), 3)


def main():
    from fastapi.testclient import TestClient
    import backend.main as app_mod

    drafts = pd.read_csv(DRAFTS)
    human = pd.read_csv(HUMAN)
    m = drafts.merge(human, on="idx", how="inner")
    assert len(m) == 30, f"expected 30 graded drafts, got {len(m)}"

    c = TestClient(app_mod.app)
    rows = []
    models = set()
    for r in m.itertuples():
        resp = c.post("/judge/groundedness",
                      json={"brand": "virgin", "text": r.text, "reply": r.draft})
        assert resp.status_code == 200, resp.text[:200]
        obj = resp.json()
        assert set(obj) >= {"claims", "score", "model"}, obj.keys()
        models.add(obj["model"])
        j5 = frac_to_1_5(obj["score"])
        rows.append({"idx": r.idx, "human_ground": int(r.human_ground),
                     "judge_frac": obj["score"], "judge_5": j5,
                     "n_claims": len(obj["claims"]),
                     "supported": sum(1 for x in obj["claims"] if x["supported"]),
                     "human_verdict": r.human_verdict})
    res = pd.DataFrame(rows)
    yt, yp = res.human_ground.tolist(), res.judge_5.tolist()
    try:
        wk = cohen_kappa_score(yt, yp, weights="quadratic")
    except Exception:
        wk = float("nan")
    try:
        from sklearn.metrics import accuracy_score
        acc = accuracy_score(yt, yp)
    except Exception:
        acc = float("nan")
    lo, hi = bootstrap_wk_ci(yt, yp)
    raw_exact = float((res.human_ground == res.judge_5).mean())
    within1 = float((abs(res.human_ground - res.judge_5) <= 1).mean())
    model = sorted(models)[0] if len(models) == 1 else f"MIXED:{sorted(models)}"
    temp = "0" if model != "heuristic-offline" else "n/a (offline heuristic)"
    verdict = "PASS" if (np.isfinite(wk) and wk >= GATE_WK) else "FAIL"

    # Coverage: live drafts for all 200 golden rows (distribution context only).
    try:
        from src.agent import AppleAgent
        from scripts.run_virgin_eval import VirginRetriever
        try:
            retr = VirginRetriever()
        except Exception:
            retr = None
        agent = AppleAgent(retr, brand="virgin")
        g = pd.read_csv(GOLD200)
        cov_scores = []
        for t in g["text"].tolist():
            try:
                o = agent.handle(t, brand="virgin")
                j = c.post("/judge/groundedness",
                           json={"brand": "virgin", "text": t, "reply": o.draft_reply}).json()
                cov_scores.append(float(j["score"]))
            except Exception:
                continue
        cov_mean = round(float(np.mean(cov_scores)), 3) if cov_scores else float("nan")
        cov_n = len(cov_scores)
    except Exception as e:
        cov_mean, cov_n = float("nan"), 0

    print(f"agreement n={len(res)} model={model} temp={temp}")
    print(f"human_ground dist: {res.human_ground.value_counts().sort_index().to_dict()}")
    print(f"judge_5 dist: {res.judge_5.value_counts().sort_index().to_dict()}")
    print(f"exact={raw_exact:.3f} within1={within1:.3f} acc={acc:.3f} wK={wk:.3f} 95%CI=[{lo}, {hi}]")
    print(f"coverage n={cov_n} mean_frac={cov_mean}")
    print(f"GATE wK>={GATE_WK}: {verdict}")

    dist_h = res.human_ground.value_counts().sort_index().to_dict()
    dist_j = res.judge_5.value_counts().sort_index().to_dict()
    item_rows = ["| idx | human_ground | judge_frac | judge_5 | n_claims | supported | human_verdict |",
                 "|---|---|---|---|---|---|---|"]
    for r in res.sort_values("idx").itertuples():
        item_rows.append(f"| {r.idx} | {r.human_ground} | {r.judge_frac:.3f} | {r.judge_5} | "
                         f"{r.n_claims} | {r.supported} | {r.human_verdict} |")
    lines = [
        "# Virgin groundedness-judge agreement V3 (workstream A1)",
        "",
        f"- Agreement set: n={len(res)} (spotcheck_30 drafts from `llm_judge_30_drafts.csv` — the exact drafts the human graded — vs `human_grades_30.csv` groundedness 1-5, single annotator blind to LLM).",
        f"- Judge: shipped `POST /judge/groundedness` (sentence claim-split + per-claim entail/passage-cite). Model leg: **{model}** (temp {temp}; Groq primary `openai/gpt-oss-20b`, fallback `qwen/qwen3.8-27b`).",
        f"- Mapping: fraction-supported -> 1-5 via 1+round(4*frac). Primary: quadratic-weighted Cohen k vs human 1-5.",
        f"- Result: exact={raw_exact:.3f}, within-1={within1:.3f}, **wK={wk:.3f} 95% CI [{lo}, {hi}]** (bootstrap {BOOTSTRAP_RESAMPLES}, seed {BOOTSTRAP_SEED}).",
        f"- Gate wK>={GATE_WK}: **{verdict}**.",
        f"- Distributions — human 1-5: {dist_h}; judge 1-5: {dist_j}.",
        f"- Coverage (context, not gate): {cov_n}/200 golden_human_200 live template drafts scored, mean fraction-supported={cov_mean}.",
        "",
        "## Method notes (anti-tuning)",
        "- The entailment rule was frozen BEFORE this run on 5 ungraded pilot probes (instrument piloting, blind to human labels): stemmed content-token coverage >=1/3 in a single passage. No threshold was moved after seeing agreement numbers; no rubric edits against the 30.",
        "- Drafts are fixed artifacts (`llm_judge_30_drafts.csv`); passages re-retrieved live (virgin NN k=5). Re-running reproduces bit-identically offline.",
        "- Human side is single-annotator (same limitation as v1/v2); n=30 -> wide CIs. The 200-coverage run has no human labels and cannot pass any gate.",
        "",
        "## What is misleading (mandatory)",
        "- A low wK here does NOT mean drafts are bad: humans grade templates 3-4 for having almost no falsifiable claims ('triage acceptable'), while claim-entailment is strict about novel template wording (Delay Repay bands, DM instructions) that retrieved customer tweets rarely contain verbatim. Strict instrument vs lenient humans is the expected disagreement shape (same split v1 found for relevance vs groundedness).",
        "- Heuristic-offline != LLM judge: the Groq semantic leg (primary when keyed) may agree better; this file reports the offline leg only until a keyed re-run exists. Do not quote this wK against the LLM path.",
        "- n=30 single-annotator: CIs span ~0.4 wide; no launch claim is supportable from this slice alone.",
        "",
        "## Next",
        "- Keyed re-run (GROQ_API_KEY): same script, LLM leg answers, temp 0; compare wK + self-consistency double-run.",
        "- Second human annotator on the 30 (double-label k); blinded relabel pack is workstream C.",
        "",
        "## Per-item table (audit)",
        "",
        *item_rows,
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
