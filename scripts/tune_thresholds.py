"""Phase 2B post-hoc decision policy for the frozen VirginTrains intent model.

Reads:
  evaluation/virgin/judge_scores_200.csv   (text + human_intent; 200 rows)
  models/intent_virgin.pkl                 (READ-ONLY: predict_proba only;
                                            NEVER retrain / NEVER overwrite)

Writes (NEW files only):
  evaluation/virgin/thresholds.json
  evaluation/virgin/per_intent_thresholds.md

Method (per-instruction research: sklearn OvR ROC/PR):
  - Score every judge text with the FROZEN pipeline (predict_proba).
  - Per intent, one-vs-rest binarization (human_intent == intent):
      sklearn.metrics.roc_curve + precision_recall_curve (+ roc_auc_score,
      average_precision_score).
  - Operating point:
      * money intents (brands.py virgin.money_intents: delay_claim,
        ticket_change_refund, fare_ticketing): precision-first — the smallest
        threshold achieving max precision subject to recall >= 0.50.
        (Pure P>=0.90 targeting collapses refund recall to 0.39 on n=200;
        the recall guard keeps the gate usable; the cost is disclosed.)
      * other intents: F1-optimal threshold (argmax of 2PR/(P+R) on the PR
        curve; ties -> smallest threshold).
  - Global MSP (max-softmax-probability) floor 0.45: aligns with the
    production low_conf gate in src/agent.py (conf < 0.45 -> escalate).
    Measured on judge-200: coverage 194/200 (0.970), covered argmax acc
    0.799 vs 0.790 unfiltered — the floor buys abstention, not accuracy.

Policy (post-hoc only, no model change):
  1. argmax intent + its probability p_pred; msp = max proba.
  2. if msp < msp_floor                     -> ABSTAIN (escalate: unresolvable/low_conf)
  3. elif p_pred < per_intent_threshold[pred] -> ABSTAIN (escalate: below_operating_point)
  4. else                                     -> ACCEPT (existing agent escalation
     rules — money_review, safety, PII, etc. — still apply downstream).

Caveats: n=200 (~14-29/intent) -> thresholds are noisy point estimates;
no held-out split (same 200 used to pick + report); re-tune on >=500
human labels before treating gates as launch-blocking.

Usage:
  .venv\\Scripts\\python.exe scripts\\tune_thresholds.py
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

ROOT = Path(__file__).resolve().parent.parent
JUDGE_CSV = ROOT / "evaluation" / "virgin" / "judge_scores_200.csv"
MODEL_PATH = ROOT / "models" / "intent_virgin.pkl"
OUT_JSON = ROOT / "evaluation" / "virgin" / "thresholds.json"
OUT_MD = ROOT / "evaluation" / "virgin" / "per_intent_thresholds.md"

MSP_FLOOR = 0.45
RECALL_GUARD = 0.50
MONEY_INTENTS = {"delay_claim", "ticket_change_refund", "fare_ticketing"}


# --------------------------------------------------------------------------- #
# Policy primitive (pure + deterministic; imported by tests).
# --------------------------------------------------------------------------- #
def apply_thresholds(pred_intent: str, proba: dict[str, float], thresholds: dict) -> dict:
    """Gate one argmax prediction through the post-hoc policy.

    proba: {intent: probability} for ALL intents (must sum ~1, need not).
    thresholds: loaded thresholds.json (uses ["msp_floor"]["value"] and
        ["per_intent"][intent]["threshold"]).

    Returns {"action": "accept"|"abstain", "reason": str,
             "msp": float, "p_pred": float, "threshold": float}.
    Deterministic: pure function of inputs (no RNG, no I/O, no model).
    """
    floor = float(thresholds["msp_floor"]["value"])
    thr = float(thresholds["per_intent"][pred_intent]["threshold"])
    msp = float(max(proba.values()))
    p_pred = float(proba[pred_intent])
    if msp < floor:
        return {"action": "abstain", "reason": "below_msp_floor",
                "msp": msp, "p_pred": p_pred, "threshold": thr}
    if p_pred < thr:
        return {"action": "abstain", "reason": "below_operating_point",
                "msp": msp, "p_pred": p_pred, "threshold": thr}
    return {"action": "accept", "reason": "above_operating_point",
            "msp": msp, "p_pred": p_pred, "threshold": thr}


# --------------------------------------------------------------------------- #
# Curve analysis.
# --------------------------------------------------------------------------- #
def _operating_point(y_true_bin: np.ndarray, scores: np.ndarray, money: bool) -> dict:
    """Chosen threshold + metrics at that point + curve summaries."""
    precision, recall, thr_pr = precision_recall_curve(y_true_bin, scores)
    fpr, tpr, thr_roc = roc_curve(y_true_bin, scores)
    roc_auc = float(roc_auc_score(y_true_bin, scores))
    ap = float(average_precision_score(y_true_bin, scores))
    # PR arrays have len(thr)+1 (last point = recall 0 edge); align.
    P, R = precision[:-1], recall[:-1]
    f1 = 2 * P * R / np.maximum(P + R, 1e-12)

    if money:
        eligible = np.where(R >= RECALL_GUARD)[0]
        pool = eligible if len(eligible) else np.arange(len(thr_pr))
        best_p = P[pool].max()
        # smallest threshold attaining best precision within pool (deterministic)
        cand = [i for i in pool if P[i] == best_p]
        j = min(cand, key=lambda i: float(thr_pr[i]))
        rule = f"max-precision s.t. recall>={RECALL_GUARD} (guarded; pure-P>=0.90 collapses refund recall)"
    else:
        best_f1 = f1.max()
        cand = [i for i in range(len(thr_pr)) if f1[i] == best_f1]
        j = min(cand, key=lambda i: float(thr_pr[i]))
        rule = "F1-optimal on PR curve (ties -> smallest threshold)"

    j = int(j)
    tp = int(((scores >= thr_pr[j]) & (y_true_bin == 1)).sum())
    fp = int(((scores >= thr_pr[j]) & (y_true_bin == 0)).sum())
    fn = int(((scores < thr_pr[j]) & (y_true_bin == 1)).sum())
    return {
        "threshold": round(float(thr_pr[j]), 4),
        "precision": round(float(P[j]), 3),
        "recall": round(float(R[j]), 3),
        "f1": round(float(f1[j]), 3),
        "support": int(y_true_bin.sum()),
        "tp": tp, "fp": fp, "fn": fn,
        "roc_auc": round(roc_auc, 3),
        "average_precision": round(ap, 3),
        "rule": rule,
        "money_tuned": bool(money),
    }


def main() -> None:
    df = pd.read_csv(JUDGE_CSV)
    obj = joblib.load(MODEL_PATH)  # read-only: no fit, no dump back
    pipe = obj["pipeline"] if isinstance(obj, dict) and "pipeline" in obj else obj
    classes = [str(c) for c in pipe.classes_]
    assert set(classes) == set(MONEY_INTENTS) | {
        "timetable_platform", "lost_property", "complaint_service",
        "accessibility_assistance", "howto_guidance",
        "support_access_followup", "other_out_of_scope",
    }, f"unexpected classes: {classes}"

    texts = df["text"].tolist()
    y = df["human_intent"].astype(str).values
    proba = np.asarray(pipe.predict_proba(texts), dtype=float)
    assert proba.shape == (len(df), len(classes))

    per_intent: dict[str, dict] = {}
    for c in classes:
        yb = (y == c).astype(int)
        s = proba[:, classes.index(c)]
        per_intent[c] = _operating_point(yb, s, money=(c in MONEY_INTENTS))

    # Global MSP floor grid (argmax policy on the same 200; descriptive only).
    msp = proba.max(axis=1)
    argmax = np.array(classes)[proba.argmax(axis=1)]
    ok = (argmax == y)
    floor_grid = {}
    for f in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
        cov = msp >= f
        floor_grid[f"{f:.2f}"] = {
            "coverage": round(float(cov.mean()), 3),
            "covered_acc": round(float(ok[cov].mean()), 3) if cov.sum() else None,
            "n_abstain": int((~cov).sum()),
        }
    cov45 = msp >= MSP_FLOOR
    payload = {
        "model": "models/intent_virgin.pkl (FROZEN — read-only predict_proba; headline acc 0.795 untouched)",
        "source": "evaluation/virgin/judge_scores_200.csv (n=200; text+human_intent)",
        "n": len(df),
        "msp_floor": {
            "value": MSP_FLOOR,
            "rationale": "aligns with production low_conf gate (src/agent.py conf<0.45); "
                         "measured coverage 0.970, covered argmax acc 0.799",
            "coverage": round(float(cov45.mean()), 3),
            "covered_argmax_acc": round(float(ok[cov45].mean()), 3),
            "grid": floor_grid,
        },
        "money_intents": sorted(MONEY_INTENTS),
        "recall_guard": RECALL_GUARD,
        "per_intent": {c: per_intent[c] for c in classes},
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # End-to-end gate preview: accept-rate + accuracy on accepted (same 200).
    thr_map = {c: per_intent[c]["threshold"] for c in classes}
    accepts, ok_acc = [], []
    for k in range(len(df)):
        pred = str(argmax[k])
        gate = float(proba[k, classes.index(pred)])
        accept = bool(msp[k] >= MSP_FLOOR and gate >= thr_map[pred])
        accepts.append(accept)
        if accept:
            ok_acc.append(bool(pred == y[k]))
    accepts = np.array(accepts)

    lines = [
        "# Virgin per-intent thresholds (post-hoc policy; model FROZEN)",
        "",
        f"Source: `evaluation/virgin/judge_scores_200.csv` (n={len(df)}). "
        "Scores: frozen `models/intent_virgin.pkl` predict_proba (read-only). "
        "Method: per-intent one-vs-rest `roc_curve` / `precision_recall_curve`; "
        "money intents precision-first (max-P s.t. recall>=0.50), others F1-optimal; "
        f"global MSP floor {MSP_FLOOR} (= production low_conf gate).",
        "",
        "## Operating points",
        "| Intent | thr | P | R | F1 | sup | ROC-AUC | AP | rule |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for c in classes:
        d = per_intent[c]
        short = "max-P,R>=.5" if d["money_tuned"] else "F1-max"
        lines.append(
            f"| {c} | {d['threshold']:.4f} | {d['precision']:.3f} | {d['recall']:.3f} | "
            f"{d['f1']:.3f} | {d['support']} | {d['roc_auc']:.3f} | "
            f"{d['average_precision']:.3f} | {short} |"
        )
    lines += [
        "",
        "## MSP floor grid (argmax policy, same 200 — descriptive, not tuned)",
        "| floor | coverage | covered acc | n abstain |",
        "|---|---|---|---|",
    ]
    for f, g in floor_grid.items():
        lines.append(f"| {f} | {g['coverage']:.3f} | {g['covered_acc']} | {g['n_abstain']} |")
    lines += [
        "",
        "## End-to-end gate preview (floor + per-intent gates, same 200)",
        f"accept-rate {accepts.mean():.3f} ({int(accepts.sum())}/200); "
        f"accuracy on accepted {(np.mean(ok_acc) if ok_acc else float('nan')):.3f}; "
        "abstentions route to escalate (unresolvable/low_conf or below_operating_point).",
        "",
        "## Caveats (mandatory)",
        "- n=200 (~14-29/intent): thresholds are noisy point estimates, no held-out split.",
        "- ticket_change_refund precision costs recall (0.867/0.565 at thr 0.708): "
        "money_review escalation still applies downstream — the gate is additive, not a replacement.",
        "- MSP floor barely moves covered accuracy (0.79->0.80): it buys abstention, not correctness.",
        "- Re-tune on >=500 human labels before launch-blocking use.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON} + {OUT_MD}")
    print(f"accept-rate {accepts.mean():.3f} acc-on-accepted "
          f"{(np.mean(ok_acc) if ok_acc else float('nan')):.3f}")


if __name__ == "__main__":
    main()
