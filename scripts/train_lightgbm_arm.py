"""Phase 2B LightGBM baseline arm (REPORT-ONLY, timeboxed).

Compares a LightGBM classifier against the FROZEN TF-IDF+LogReg
(models/intent_virgin.pkl, headline acc 0.795 — NEVER retrained/replaced)
on the human-200 headline set.

Reads (read-only):
  data/processed/virgin_inbound_pool.csv   (same <=30k weak sample as
                                            scripts/train_virgin.py: n=30000,
                                            seed=42, first-match weak labels)
  evaluation/virgin/golden_human_200.csv   (headline labels: human_intent)
  models/intent_virgin.pkl                 (predict only)

Writes (NEW file only):
  evaluation/virgin/lightgbm_report.md

Design (per LightGBM docs, sklearn-compatible API):
  - Fresh TfidfVectorizer with IDENTICAL params to scripts/train_virgin.py
    ((1,2)-grams, min_df=3, max_features=30000, sublinear_tf, normalize
    preprocessor) fit on the same 30k weak sample -> same matrix shape.
  - Stratified 90/10 train/val split (seed 42); LGBMClassifier multiclass,
    num_leaves=31 + min_child_samples=100 (capped: sparse 30k-dim TF-IDF
    must not grow deep singleton leaves), lr=0.05, n_estimators<=500 with
    lightgbm.early_stopping(50) on val multi_logloss.
  - Head-to-head on human-200: acc + macro-F1 per arm; percentile bootstrap
    95% CIs (2000 resamples, seed 20260912 — same convention as
    scripts/run_virgin_eval.py) on LGBM-minus-LogReg deltas.
  - Verdict rule (fixed before seeing numbers): SHIP iff the macro-F1 delta
    CI lies strictly above 0; else NO-SHIP. Report-only: no model artifact
    is written, nothing is wired into src/agent.py.

Timebox: MAX_SECONDS=600 wall-clock for the fit; chosen hyperparams fit in
~1-3 min CPU on this matrix (measured and recorded in the report).

Usage:
  C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\train_lightgbm_arm.py
  (requires lightgbm==4.7.0 in .venv; PYTHONPATH=C:\\Hiver)
"""

from __future__ import annotations

import time
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split

from src.agent import _weak_label_generic
from src.text_norm import normalize
from src.virgin_intents import INTENTS, KEYWORDS

ROOT = Path(__file__).resolve().parent.parent
POOL = ROOT / "data" / "processed" / "virgin_inbound_pool.csv"
GOLDEN_HUMAN = ROOT / "evaluation" / "virgin" / "golden_human_200.csv"
MODEL_PATH = ROOT / "models" / "intent_virgin.pkl"
OUT_MD = ROOT / "evaluation" / "virgin" / "lightgbm_report.md"

N_WEAK = 30000
SEED = 42
VAL_FRACTION = 0.10
MAX_SECONDS = 600  # timebox for the LGBM fit
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20260912  # same convention as scripts/run_virgin_eval.py

LGBM_PARAMS = {
    "objective": "multiclass",
    "num_class": len(INTENTS),
    "num_leaves": 31,          # capped
    "min_child_samples": 100,  # capped (min_data): no singleton leaves on sparse TF-IDF
    "learning_rate": 0.05,
    "n_estimators": 500,
    "reg_lambda": 1.0,
    "deterministic": True,
    "random_state": SEED,
    "n_jobs": -1,
    "verbosity": -1,
}


def weak_sample(n: int = N_WEAK, seed: int = SEED) -> pd.DataFrame:
    df = pd.read_csv(POOL, usecols=["text"]).dropna()
    df = df.sample(min(n, len(df)), random_state=seed).reset_index(drop=True)
    df["weak"] = [_weak_label_generic(t, KEYWORDS) for t in df.text.tolist()]
    return df


def bootstrap_delta_ci(y_true: list, p_logreg: list, p_lgbm: list,
                       n_resamples: int = BOOTSTRAP_RESAMPLES,
                       seed: int = BOOTSTRAP_SEED) -> dict:
    """Percentile 95% CIs for (LGBM-LogReg) deltas on acc/macroF1. Deterministic."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    yt = np.array(y_true, dtype=object)
    a = np.array(p_logreg, dtype=object)
    b = np.array(p_lgbm, dtype=object)
    deltas = {"acc": [], "macroF1": []}
    for _ in range(n_resamples):
        idx = rng.integers(0, n, n)
        deltas["acc"].append(accuracy_score(yt[idx], b[idx]) - accuracy_score(yt[idx], a[idx]))
        deltas["macroF1"].append(
            f1_score(yt[idx], b[idx], average="macro", zero_division=0)
            - f1_score(yt[idx], a[idx], average="macro", zero_division=0))
    return {k: (round(float(np.percentile(v, 2.5)), 3),
                round(float(np.percentile(v, 97.5)), 3)) for k, v in deltas.items()}


def main() -> None:
    t_all = time.perf_counter()
    print(f"lightgbm {lgb.__version__}; params={LGBM_PARAMS}")

    # 1. Same 30k weak sample + same TF-IDF recipe as scripts/train_virgin.py.
    df = weak_sample()
    print(f"pool_sample={len(df)} (seed {SEED}, cap {N_WEAK})")
    vec = TfidfVectorizer(preprocessor=normalize, lowercase=False,
                          ngram_range=(1, 2), min_df=3, max_features=30000,
                          sublinear_tf=True)
    X = vec.fit_transform(df.text.tolist())
    print(f"tfidf matrix {X.shape} nnz={X.nnz}")
    y = np.array([INTENTS.index(w) for w in df.weak.tolist()], dtype=int)

    Xtr, Xva, ytr, yva = train_test_split(
        X, y, test_size=VAL_FRACTION, random_state=SEED, stratify=y)

    # 2. Timeboxed LightGBM fit with early stopping on val multi_logloss.
    clf = lgb.LGBMClassifier(**LGBM_PARAMS)
    t0 = time.perf_counter()
    clf.fit(Xtr, ytr, eval_X=Xva, eval_y=yva,
            callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)])
    fit_s = time.perf_counter() - t0
    print(f"fit {fit_s:.1f}s (budget {MAX_SECONDS}s); best_iteration={clf.best_iteration_}")
    assert fit_s < MAX_SECONDS, f"TIMEBOX EXCEEDED: {fit_s:.1f}s >= {MAX_SECONDS}s"

    # 3. Head-to-head on human-200 (frozen LogReg read-only).
    gh = pd.read_csv(GOLDEN_HUMAN)
    texts = gh.text.tolist()
    y_true = gh.human_intent.astype(str).tolist()
    obj = joblib.load(MODEL_PATH)
    pipe = obj["pipeline"] if isinstance(obj, dict) and "pipeline" in obj else obj
    p_lr = [str(p) for p in pipe.predict(texts)]
    Xh = vec.transform(texts)
    p_lgb = [INTENTS[int(i)] for i in clf.predict(Xh)]

    acc_lr, acc_lgb = accuracy_score(y_true, p_lr), accuracy_score(y_true, p_lgb)
    f1_lr = f1_score(y_true, p_lr, average="macro", zero_division=0)
    f1_lgb = f1_score(y_true, p_lgb, average="macro", zero_division=0)
    ci = bootstrap_delta_ci(y_true, p_lr, p_lgb)
    _, _, f_lr, sup = precision_recall_fscore_support(
        y_true, p_lr, labels=INTENTS, zero_division=0)
    _, _, f_lgb, _ = precision_recall_fscore_support(
        y_true, p_lgb, labels=INTENTS, zero_division=0)

    # 4. Verdict (rule fixed a priori): SHIP iff macro-F1 delta CI > 0.
    lo, hi = ci["macroF1"]
    verdict = "SHIP" if lo > 0 else "NO-SHIP"

    md = [
        "# LightGBM baseline arm vs frozen LogReg (report-only, Phase 2B)",
        "",
        f"Config: LGBMClassifier {LGBM_PARAMS} + early_stopping(50) on val "
        f"multi_logloss; {N_WEAK} weak sample (seed {SEED}), TF-IDF recipe identical "
        "to scripts/train_virgin.py; stratified 90/10 train/val (seed 42). "
        f"Fit wall-time {fit_s:.1f}s (budget {MAX_SECONDS}s); "
        f"best_iteration={clf.best_iteration_}; lightgbm=={lgb.__version__}.",
        f"Frozen reference: models/intent_virgin.pkl (predict-only; headline acc 0.795 untouched).",
        "Note: LogReg 0.790 here = raw pipeline predict on human-200; the 0.795 headline "
        "adds agent-side crowd-remap/language gates (identical frozen weights). "
        "Both arms scored as raw classifiers for a like-for-like comparison.",
        f"Eval: evaluation/virgin/golden_human_200.csv (n={len(gh)}); "
        f"bootstrap {BOOTSTRAP_RESAMPLES} resamples seed {BOOTSTRAP_SEED} "
        "(same convention as run_virgin_eval.py).",
        "",
        "## Head-to-head (human-200)",
        "| Arm | acc | macro-F1 |",
        "|---|---|---|",
        f"| LogReg (frozen) | {acc_lr:.3f} | {f1_lr:.3f} |",
        f"| LightGBM (new) | {acc_lgb:.3f} | {f1_lgb:.3f} |",
        f"| Delta (LGBM-LogReg) | {acc_lgb - acc_lr:+.3f} 95% CI [{ci['acc'][0]:+.3f}, {ci['acc'][1]:+.3f}] "
        f"| {f1_lgb - f1_lr:+.3f} 95% CI [{lo:+.3f}, {hi:+.3f}] |",
        "",
        "## Per-intent F1 (LogReg vs LGBM; support in brackets)",
        "| Intent | LogReg F1 | LGBM F1 | Delta |",
        "|---|---|---|---|",
    ]
    for c, a, b, s in zip(INTENTS, f_lr, f_lgb, sup):
        md.append(f"| {c} | {a:.3f} ({s}) | {b:.3f} ({s}) | {b - a:+.3f} |")
    md += [
        "",
        f"## Verdict: {verdict}",
        "Rule (fixed a priori): SHIP iff macro-F1 Delta 95% CI lies strictly above 0; "
        "else NO-SHIP. Report-only arm: no artifact written, nothing wired into "
        "src/agent.py. Small-n caveat (n=200, ~14-29/intent) applies to both arms equally.",
        "",
        "## What this does NOT claim",
        "- Weak-30k training labels are keyword-bootstrapped (circular by construction); "
        "the comparison measures headroom of a stronger learner on weak signal, not quality gains.",
        "- No calibration / threshold analysis was done for the LGBM arm (see thresholds.json for LogReg).",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    total = time.perf_counter() - t_all
    print(f"LogReg acc={acc_lr:.3f} F1={f1_lr:.3f} | LGBM acc={acc_lgb:.3f} F1={f1_lgb:.3f}")
    print(f"LGBM-LogReg Delta-acc 95% CI [{ci['acc'][0]:+.3f}, {ci['acc'][1]:+.3f}], "
          f"Delta-F1 95% CI [{lo:+.3f}, {hi:+.3f}] -> {verdict}")
    print(f"wrote {OUT_MD} (total {total:.1f}s)")


if __name__ == "__main__":
    main()
