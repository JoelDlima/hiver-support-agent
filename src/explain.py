"""Phase 2B explainability for the frozen VirginTrains TF-IDF + LogReg model.

READ-ONLY w.r.t. models/intent_virgin.pkl (loads pipeline, never fits/saves).

Two surfaces (both JSON-serializable, for UI consumption):
  1. top_coefficients(intent, k) — global: top +k / -k TF-IDF features by
     LogReg coefficient weight for one intent.
  2. explain_text(text, ...) — local: EXACT linear-SHAP hand-computed
     (no `shap` dependency). For a linear logit

         logit_c(x) = b_c + sum_j beta_cj * x_j

     with background mean E[x] over a fixed background corpus, the exact
     Shapley values of a linear model are

         phi_cj = beta_cj * (x_j - E[x]_j),

     so that  b_c + beta_c.E[x] + sum_j phi_cj == logit_c(x)  exactly
     (verified per call; residual reported as exactness.abs_err).
     Default background: evaluation/virgin/judge_scores_200.csv texts
     (n=200, same set the Phase-2B thresholds were tuned on; documented in
     every output under "background").

Usage:
  C:\\Hiver\\.venv\\Scripts\\python.exe -m src.explain "my train was delayed ..."
"""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Sequence

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "intent_virgin.pkl"
BACKGROUND_CSV = ROOT / "evaluation" / "virgin" / "judge_scores_200.csv"


@lru_cache(maxsize=1)
def _load_pipeline():
    obj = joblib.load(MODEL_PATH)  # read-only
    pipe = obj["pipeline"] if isinstance(obj, dict) and "pipeline" in obj else obj
    return pipe


def _parts():
    pipe = _load_pipeline()
    tfidf = pipe.named_steps["tfidf"]
    clf = pipe.named_steps["clf"]
    classes = [str(c) for c in clf.classes_]
    feats = [str(f) for f in tfidf.get_feature_names_out()]
    beta = np.asarray(clf.coef_, dtype=float)          # (C, F)
    intercept = np.asarray(clf.intercept_, dtype=float)  # (C,)
    return pipe, tfidf, clf, classes, feats, beta, intercept


@lru_cache(maxsize=4)
def _background_mean(n_rows: int = 200) -> tuple[np.ndarray, dict]:
    """Mean TF-IDF vector E[x] over the background corpus (dense, (F,))."""
    pipe, tfidf, *_ = _parts()
    df = pd.read_csv(BACKGROUND_CSV, usecols=["text"])
    texts = df["text"].astype(str).tolist()[:n_rows]
    Xb = tfidf.transform(texts)  # (n, F) sparse
    mean = np.asarray(Xb.mean(axis=0)).ravel()
    meta = {"source": "evaluation/virgin/judge_scores_200.csv", "n": len(texts)}
    return mean, meta


# --------------------------------------------------------------------------- #
# 1. Global coefficients.
# --------------------------------------------------------------------------- #
def top_coefficients(intent: str, k: int = 10) -> dict:
    """Top +k / -k TF-IDF features by LogReg weight for `intent`."""
    _, _, _, classes, feats, beta, _ = _parts()
    if intent not in classes:
        raise ValueError(f"unknown intent {intent!r}; classes={classes}")
    w = beta[classes.index(intent)]
    order_pos = np.argsort(-w, kind="stable")[:k]
    order_neg = np.argsort(w, kind="stable")[:k]
    return {
        "intent": intent,
        "k": int(k),
        "top_positive": [{"feature": feats[j], "weight": round(float(w[j]), 6)}
                         for j in order_pos],
        "top_negative": [{"feature": feats[j], "weight": round(float(w[j]), 6)}
                         for j in order_neg],
    }


# --------------------------------------------------------------------------- #
# 2. Local exact linear-SHAP.
# --------------------------------------------------------------------------- #
def explain_text(text: str, intent: str | None = None, top_k: int = 10,
                 background_texts: Sequence[str] | None = None) -> dict:
    """Hand-computed exact linear-SHAP for one text (JSON-serializable).

    intent: target class (default: argmax prediction). top_k: contributions
    kept in top_positive/top_negative (full nonzero list in contributions).
    background_texts: override background corpus (default: judge-200 mean).
    """
    pipe, tfidf, _, classes, feats, beta, intercept = _parts()
    x = tfidf.transform([text or ""])                      # (1, F) sparse
    logits = (intercept + np.asarray(x.dot(beta.T)).ravel())  # (C,)
    ex = np.exp(logits - logits.max())
    proba = ex / ex.sum()
    pred_idx = int(np.argmax(logits))
    tgt_idx = pred_idx if intent is None else classes.index(str(intent))
    tgt = classes[tgt_idx]

    if background_texts is None:
        mean, bg_meta = _background_mean()
    else:
        Xb = tfidf.transform(list(background_texts))
        mean = np.asarray(Xb.mean(axis=0)).ravel()
        bg_meta = {"source": "caller-provided", "n": len(background_texts)}

    b = beta[tgt_idx]                       # (F,)
    xv = x.toarray().ravel()                # dense row; F=30k is cheap
    phi = b * (xv - mean)                   # EXACT linear-SHAP values
    base = float(intercept[tgt_idx] + b.dot(mean))
    logit = float(logits[tgt_idx])
    abs_err = abs((base + float(phi.sum())) - logit)

    nz = np.where(xv != 0.0)[0]
    contribs = [{
        "feature": feats[j],
        "tfidf": round(float(xv[j]), 6),
        "mean_tfidf": round(float(mean[j]), 6),
        "weight": round(float(b[j]), 6),
        "phi": round(float(phi[j]), 6),
    } for j in nz]
    contribs.sort(key=lambda d: d["phi"], reverse=True)
    return {
        "text": text,
        "predicted_intent": classes[pred_idx],
        "predicted_proba": round(float(proba[pred_idx]), 4),
        "target_intent": tgt,
        "target_proba": round(float(proba[tgt_idx]), 4),
        "all_proba": {c: round(float(p), 4) for c, p in zip(classes, proba)},
        "logit": round(logit, 6),
        "base_value": round(base, 6),
        "background": bg_meta,
        "nonzero_features": int(len(nz)),
        "contributions": contribs,
        "top_positive": contribs[:top_k],
        "top_negative": contribs[::-1][:top_k],
        "global": top_coefficients(tgt, k=top_k),
        "exactness": {
            "sum_phi_plus_base": round(base + float(phi.sum()), 6),
            "logit": round(logit, 6),
            "abs_err": abs_err,
        },
    }


def explain_json(text: str, intent: str | None = None, top_k: int = 10) -> str:
    return json.dumps(explain_text(text, intent=intent, top_k=top_k), indent=2)


def main(argv: list[str]) -> None:
    text = argv[1] if len(argv) > 1 else "my train was delayed, I want to claim compensation"
    print(explain_json(text))


if __name__ == "__main__":
    main(sys.argv)
