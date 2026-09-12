"""VirginTrains SetFit/MiniLM CHALLENGER head (Phase 2A, report-only).

 contrasts the frozen TF-IDF+LogReg baseline (`models/intent_virgin.pkl`, 0.795
 acc / 0.803 macro-F1 on 200 gold) with a frozen-body embedding head:

 * body  — `paraphrase-MiniLM-L6-v2` via sentence-transformers 6.0.1, FROZEN
   (never fine-tuned; this is the same starting body SetFit 1.2.0 uses, but the
   contrastive body-tuning phase is deliberately skipped so the challenger is
   a pure head-to-head on the classifier: TF-IDF features vs MiniLM features).
 * head  — sklearn LogisticRegression, i.e. SetFit's default classifier head
   (SetFit 1.2.0 `SetFitModel` head is LogReg; same hyperparams as the TF-IDF
   baseline: max_iter=1000, C=2.0, class_weight="balanced").
 * "SetFit-style" weak-pretrain — the head is first fit on a CLASS-BALANCED
   subsample of the 30k weak labels (equal pairs per class mirrors SetFit's
   `samples_per_label` few-shot sampling spirit), then warm-started
   (sklearn `warm_start`) and fine-tuned on the 200 human labels.
 * calibration — single temperature T fit on out-of-fold (OOF) logits
   (5x stratified CV) by NLL grid search.
 * abstention — MSP and Energy scores with a coverage curve; report-only, the
   production agent is untouched.

 Report-only: importing this module never touches `models/intent_virgin.pkl`,
 goldens, `run_virgin_eval.py`, or the frontend. Lazy body loading: import is
 light; the ST model loads on first `embed()` call.

 Pinned deps (Phase 2A rule): setfit==1.2.0, sentence-transformers==6.0.1,
 torch CPU (auto-dep). Verified against setfit 1.x docs (SetFitTrainer two
 phases: contrastive body finetune + LogReg head) and sentence-transformers
 docs (`SentenceTransformer.encode`); we implement phase 2 only, on a frozen
 phase-1 body.
 """

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Sequence

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

from .virgin_intents import INTENTS

MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L6-v2"
EMBED_DIM = 384
ARTIFACT_DIR = Path(r"C:\Hiver\models\intent_virgin_setfit")
SEED = 42

# Same head hyperparams as the TF-IDF baseline (scripts/train_virgin.py) so the
# CV comparison isolates the feature change (TF-IDF -> MiniLM), not the solver.
HEAD_C = 2.0
HEAD_MAX_ITER = 1000
CV_FOLDS = 5
ABSTAIN_LABEL = "abstain"

# Balanced weak-pretrain budget: equal samples per intent (SetFit-style
# few-shot balanced sampling). 400/intent x 10 = 4000 rows; the rarest weak
# intent (accessibility_assistance, 167/30k) is fully included, the rest are
# subsampled with SEED.
WEAK_PER_CLASS = 400

REQUIRED_SETFIT = "1.2.0"
REQUIRED_ST = "6.0.1"

_body = None


def check_versions() -> dict:
    """Return installed {setfit, sentence_transformers, torch} versions.

    The train script asserts these equal the Phase 2A pins; the pinned
    packages are real imports used below (SetFit parity documented via the
    shared LogReg-head design; embeddings via sentence-transformers).
    """
    import setfit
    import sentence_transformers
    import torch

    return {
        "setfit": getattr(setfit, "__version__", "unknown"),
        "sentence_transformers": getattr(sentence_transformers, "__version__", "unknown"),
        "torch": getattr(torch, "__version__", "unknown"),
        "torch_cuda": bool(torch.cuda.is_available()),
    }


def get_body():
    """Load (once) the frozen MiniLM body. Never trained — encode only."""
    global _body
    if _body is None:
        from sentence_transformers import SentenceTransformer

        _body = SentenceTransformer(MODEL_NAME)
        _body.eval()
    return _body


def embed(texts: Sequence[str], batch_size: int = 64) -> np.ndarray:
    """Encode texts with the frozen body -> (n, 384) float32 array."""
    body = get_body()
    safe = [(t if isinstance(t, str) and t.strip() else "") for t in texts]
    return np.asarray(
        body.encode(safe, batch_size=batch_size, show_progress_bar=False,
                    convert_to_numpy=True, normalize_embeddings=False),
        dtype=np.float32,
    )


def build_head() -> LogisticRegression:
    """Fresh classifier head (SetFit default: LogReg, baseline hyperparams)."""
    return LogisticRegression(max_iter=HEAD_MAX_ITER, C=HEAD_C,
                              class_weight="balanced", random_state=SEED)


def balanced_weak_sample(y: Sequence[str], per_class: int = WEAK_PER_CLASS,
                         seed: int = SEED) -> np.ndarray:
    """Indices of a class-balanced weak subsample (all rows of rare classes)."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y, dtype=object)
    keep: list[int] = []
    for label in INTENTS:
        idx = np.flatnonzero(y == label)
        if len(idx) == 0:
            continue
        if len(idx) <= per_class:
            keep.extend(idx.tolist())
        else:
            keep.extend(rng.choice(idx, size=per_class, replace=False).tolist())
    return np.asarray(sorted(keep), dtype=int)


def weak_pretrain(X: np.ndarray, y: Sequence[str]) -> LogisticRegression:
    """Fit the head on the class-balanced weak subsample."""
    sel = balanced_weak_sample(y)
    head = build_head()
    head.fit(X[sel], np.asarray(y, dtype=object)[sel])
    return head


def finetune_from(head: LogisticRegression, X: np.ndarray,
                  y: Sequence[str]) -> LogisticRegression:
    """Warm-start `head` (weak-pretrained) and fine-tune on human labels.

    Falls back to a fresh fit if classes mismatch (defensive; does not occur
    on the virgin 30k/200 pair, both cover all 10 intents).
    """
    y = np.asarray(y, dtype=object)
    tuned = build_head()
    try:
        if list(getattr(head, "classes_", [])) == list(INTENTS):
            tuned.coef_ = np.array(head.coef_, dtype=float)
            tuned.intercept_ = np.array(head.intercept_, dtype=float)
            tuned.classes_ = np.array(head.classes_, dtype=object)
            tuned.warm_start = True
    except Exception:
        tuned.warm_start = False
    tuned.fit(X, y)
    return tuned


def _softmax(logits: np.ndarray) -> np.ndarray:
    z = np.asarray(logits, dtype=float)
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def scaled_proba(head: LogisticRegression, X: np.ndarray,
                 temperature: float = 1.0) -> np.ndarray:
    """Temp-scaled softmax over head logits (T=1.0 == plain predict_proba)."""
    logits = np.asarray(head.decision_function(X), dtype=float)
    if logits.ndim == 1:  # binary fallback (never on 10-class virgin head)
        logits = np.stack([-logits, logits], axis=1)
    return _softmax(logits / float(temperature))


def fit_temperature(oof_logits: np.ndarray, oof_true: Sequence[int],
                    grid: Sequence[float] | None = None) -> float:
    """Pick T minimizing NLL on OOF logits (grid search, deterministic)."""
    if grid is None:
        grid = [round(t, 2) for t in
                list(np.arange(0.1, 1.0, 0.1)) + list(np.arange(1.0, 5.05, 0.1))]
    y = np.asarray(oof_true, dtype=int)
    logits = np.asarray(oof_logits, dtype=float)
    best_t, best_nll = 1.0, float("inf")
    n = len(y)
    for t in grid:
        p = _softmax(logits / float(t))
        nll = -float(np.log(np.clip(p[np.arange(n), y], 1e-12, 1.0)).mean())
        if nll < best_nll:
            best_nll, best_t = nll, float(t)
    return best_t


def confidence_scores(proba: np.ndarray, logits: np.ndarray | None = None,
                      temperature: float = 1.0,
                      mode: str = "msp") -> np.ndarray:
    """Selective-prediction confidence: 'msp' or 'energy' (higher = surer).

    Energy E(x) = -T * logsumexp(logit / T); confidence reported as -E so
    that, like MSP, higher means more confident (standard selective-pred
    convention; Guo et al. 2017 for T-scaling, Liu et al. 2020 for energy).
    """
    p = np.asarray(proba, dtype=float)
    if mode == "msp":
        return p.max(axis=1)
    if mode == "energy":
        if logits is None:
            logits = np.log(np.clip(p, 1e-12, 1.0))
            t = 1.0
        else:
            logits = np.asarray(logits, dtype=float)
            t = float(temperature)
        # logsumexp over classes, scaled: -E = T * logsumexp(z / T)
        z = logits / t
        return t * (np.log(np.exp(z - z.max(axis=1, keepdims=True)).sum(axis=1))
                    + z.max(axis=1))
    raise ValueError(f"unknown mode {mode!r} (want 'msp' or 'energy')")


def coverage_curve(y_true: Sequence[str], y_pred: Sequence[str],
                   confidence: Sequence[float],
                   grid: Sequence[float] = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
                   ) -> list[dict]:
    """Selective-risk curve: for each min-confidence level, coverage + acc.

    Rows sorted desc by `grid`; each row = top fraction with conf >= level.
    """
    yt = np.asarray(y_true, dtype=object)
    yp = np.asarray(y_pred, dtype=object)
    c = np.asarray(confidence, dtype=float)
    ok = (yt == yp)
    out = []
    for level in grid:
        mask = c >= float(level)
        cov = float(mask.mean()) if len(mask) else 0.0
        acc = float(ok[mask].mean()) if mask.sum() else float("nan")
        out.append({"min_conf": round(float(level), 2),
                    "coverage": round(cov, 3),
                    "selective_acc": round(acc, 3) if mask.sum() else None,
                    "n": int(mask.sum())})
    return out


def coverage_at_accuracy(y_true: Sequence[str], y_pred: Sequence[str],
                         confidence: Sequence[float],
                         target: float = 0.90) -> dict:
    """Max coverage whose top-k-by-confidence slice keeps acc >= target."""
    yt = np.asarray(y_true, dtype=object)
    yp = np.asarray(y_pred, dtype=object)
    c = np.asarray(confidence, dtype=float)
    order = np.argsort(-c, kind="stable")
    ok = (yt[order] == yp[order]).astype(float)
    cum_acc = np.cumsum(ok) / np.arange(1, len(ok) + 1)
    good = np.flatnonzero(cum_acc >= float(target))
    if len(good) == 0:
        return {"target_acc": target, "coverage": 0.0, "n": 0,
                "achieved_acc": None}
    k = int(good.max()) + 1
    return {"target_acc": target, "coverage": round(k / len(ok), 3), "n": k,
            "achieved_acc": round(float(cum_acc[k - 1]), 3)}


# ---------------------------------------------------------------- artifact IO

def save_artifact(directory: Path | str, head_final: LogisticRegression,
                  head_weak: LogisticRegression, temperature: float,
                  meta: dict) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    joblib.dump(head_final, directory / "head_final.joblib")
    joblib.dump(head_weak, directory / "head_weak.joblib")
    (directory / "labels.json").write_text(json.dumps(INTENTS), encoding="utf-8")
    full_meta = {"model_name": MODEL_NAME, "embed_dim": EMBED_DIM,
                 "temperature": float(temperature),
                 "setfit_pin": REQUIRED_SETFIT, "st_pin": REQUIRED_ST,
                 "versions": check_versions(), **meta}
    (directory / "meta.json").write_text(json.dumps(full_meta, indent=2),
                                         encoding="utf-8")
    return directory


def load_artifact(directory: Path | str = ARTIFACT_DIR) -> dict:
    """Load challenger artifact (head only; body lazy-loads on predict)."""
    directory = Path(directory)
    labels = json.loads((directory / "labels.json").read_text(encoding="utf-8"))
    meta = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
    return {"labels": labels, "meta": meta,
            "temperature": float(meta.get("temperature", 1.0)),
            "head": joblib.load(directory / "head_final.joblib")}


def predict(texts: Sequence[str], artifact: dict,
            batch_size: int = 64) -> dict:
    """Predict intents: {labels, proba (temp-scaled), confidence_msp,
    confidence_energy, latency_ms}."""
    t0 = time.perf_counter()
    X = embed(list(texts), batch_size=batch_size)
    head = artifact["head"]
    labels = list(artifact["labels"])
    temp = float(artifact.get("temperature", 1.0))
    proba = scaled_proba(head, X, temperature=temp)
    logits = np.asarray(head.decision_function(X), dtype=float)
    idx = proba.argmax(axis=1)
    lat = (time.perf_counter() - t0) * 1000
    return {
        "labels": [labels[i] for i in idx],
        "proba": proba,
        "confidence_msp": confidence_scores(proba, mode="msp"),
        "confidence_energy": confidence_scores(proba, logits=logits,
                                               temperature=temp, mode="energy"),
        "latency_ms": lat,
    }


def predict_with_abstention(texts: Sequence[str], artifact: dict,
                            threshold: float = 0.6,
                            mode: str = "msp") -> list[str]:
    """Predict, abstaining (label 'abstain') when confidence < threshold."""
    out = predict(texts, artifact)
    conf = out["confidence_msp"] if mode == "msp" else out["confidence_energy"]
    if mode == "energy":
        # energy confidences are unnormalised; threshold is a quantile-free
        # raw cut — callers should calibrate it from the coverage curve.
        return [l if c >= threshold else ABSTAIN_LABEL
                for l, c in zip(out["labels"], conf)]
    return [l if float(c) >= float(threshold) else ABSTAIN_LABEL
            for l, c in zip(out["labels"], conf)]
