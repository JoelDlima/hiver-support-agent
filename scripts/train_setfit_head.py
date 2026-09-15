"""Train the VirginTrains SetFit/MiniLM CHALLENGER head (Phase 2A, report-only).

 Pipeline (frozen body throughout — the MiniLM weights are never updated):
   1. weak pool: same 30k sample (seed 42) + weak rules as scripts/train_virgin.py
   2. embed weak (MiniLM, frozen) -> weak-pretrain LogReg head on a
      class-balanced subsample (SetFit-style few-shot sampling)
   3. embed 200 human labels -> 5x stratified CV (seed 42): per fold,
      warm-start from the weak head, fine-tune on 160, test on 40 (OOF)
   4. fit temperature T on OOF logits (NLL grid); bootstrap 95% CIs on OOF
      acc / macro-F1 (2000 resamples, seed 20260912 — same convention as
      scripts/run_virgin_eval.py)
   5. coverage curve (MSP/Energy) + coverage@90% on temp-scaled OOF
   6. refit final head (warm-start) on all 200; write artifact

 Writes ONLY models/intent_virgin_setfit/ (+ stdout). Never touches
 models/intent_virgin.pkl, goldens, evaluation CSVs, or the frontend.

 Usage: PYTHONPATH=C:\\Hiver C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\train_setfit_head.py
 """

import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold

from src.agent import _weak_label_generic
from src.virgin_intents import INTENTS, KEYWORDS
from src import setfit_head as sh

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "data" / "processed" / "virgin_inbound_pool.csv"
GOLDEN_HUMAN = ROOT / "evaluation" / "virgin" / "golden_human_200.csv"
BASELINE_CSV = ROOT / "evaluation" / "virgin" / "results_human200.csv"  # read-only
OUT_DIR = sh.ARTIFACT_DIR
CACHE_DIR = OUT_DIR / "_cache"

BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20260912


def _bootstrap_ci(y_true, y_pred, metric, n=BOOTSTRAP_RESAMPLES, seed=BOOTSTRAP_SEED):
    rng = np.random.default_rng(seed)
    yt = np.asarray(y_true, dtype=object)
    yp = np.asarray(y_pred, dtype=object)
    vals = []
    for _ in range(n):
        idx = rng.integers(0, len(yt), len(yt))
        vals.append(metric(yt[idx].tolist(), yp[idx].tolist()))
    return round(float(np.percentile(vals, 2.5)), 3), round(float(np.percentile(vals, 97.5)), 3)


def _embed_cached(texts, key):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    f = CACHE_DIR / f"{key}.npy"
    if f.exists():
        print(f"cache hit: {f} (delete to re-embed)")
        return np.load(f)
    X = sh.embed(texts)
    np.save(f, X)
    print(f"embedded {len(texts)} -> {f} {X.shape}")
    return X


def main():
    t_all = time.perf_counter()
    vers = sh.check_versions()
    print("versions:", vers)
    assert vers["setfit"] == sh.REQUIRED_SETFIT, vers
    assert vers["sentence_transformers"] == sh.REQUIRED_ST, vers
    assert not vers["torch_cuda"], "CPU-only rule violated"

    # 1-2. weak 30k (same sample + rules as train_virgin.py) + embed + pretrain
    df = pd.read_csv(POOL, usecols=["text"]).dropna()
    df = df.sample(min(30000, len(df)), random_state=42).reset_index(drop=True)
    weak = [_weak_label_generic(t, KEYWORDS) for t in df.text.tolist()]
    print(f"pool_sample={len(df)} (seed 42, cap 30000)")
    print(pd.Series(weak).value_counts().to_string())
    Xw = _embed_cached(df.text.tolist(), "weak30k")
    head_weak = sh.weak_pretrain(Xw, weak)
    sel = sh.balanced_weak_sample(weak)
    print(f"weak-pretrain rows={len(sel)} "
          f"({pd.Series(np.asarray(weak)[sel]).value_counts().min()}/class target {sh.WEAK_PER_CLASS})")
    print("weak-head train acc (vs weak, circular, optimistic):",
          round(accuracy_score(weak, head_weak.predict(Xw)), 3))

    # 3. human 200 + CV
    gh = pd.read_csv(GOLDEN_HUMAN)
    texts = gh.text.tolist()
    yh = gh.human_intent.tolist()
    Xh = _embed_cached(texts, "human200")

    # Weak-head-only transfer (diagnostic, apples-to-apples with the TF-IDF
    # baseline: weak-trained head tested on human-200, no human fitting).
    hw_pred = head_weak.predict(Xh)
    hw_acc = accuracy_score(yh, hw_pred)
    hw_mac = f1_score(yh, hw_pred, average="macro", zero_division=0)
    print(f"weak-head-only transfer human-200: acc={hw_acc:.3f} macroF1={hw_mac:.3f}")

    skf = StratifiedKFold(n_splits=sh.CV_FOLDS, shuffle=True, random_state=sh.SEED)
    oof_pred = np.empty(len(yh), dtype=object)
    oof_logits = np.zeros((len(yh), len(INTENTS)))
    oof_classes: list | None = None
    fold_rows = []
    for fold, (tr, te) in enumerate(skf.split(Xh, yh)):
        tuned = sh.finetune_from(head_weak, Xh[tr], np.asarray(yh)[tr].tolist())
        pred = list(tuned.predict(Xh[te]))
        oof_pred[te] = pred  # aligned store (fold-test order != dataset order)
        if oof_classes is None:
            oof_classes = list(tuned.classes_)
        assert list(tuned.classes_) == oof_classes, (fold, tuned.classes_)
        oof_logits[te] = np.asarray(tuned.decision_function(Xh[te]), dtype=float)
        acc = accuracy_score(np.asarray(yh)[te], pred)
        mac = f1_score(np.asarray(yh)[te], pred, average="macro", zero_division=0)
        fold_rows.append({"fold": fold, "n_train": len(tr), "n_test": len(te),
                          "acc": round(float(acc), 3), "macroF1": round(float(mac), 3)})
        print(f"fold {fold}: acc={acc:.3f} macroF1={mac:.3f}")
    assert oof_classes == sorted(INTENTS), oof_classes  # sklearn sorts classes_

    # Honest regularization ablation (aligned OOF; same protocol, C varies).
    # Answers "is C=2.0 the problem?" — kept out of the headline number.
    ablation = {}
    for C in (0.1, 0.5):
        pa = np.empty(len(yh), dtype=object)
        for tr, te in skf.split(Xh, yh):
            c = LogisticRegression(max_iter=1000, C=C, class_weight="balanced",
                                   random_state=42).fit(Xh[tr], np.asarray(yh)[tr].tolist())
            pa[te] = list(c.predict(Xh[te]))
        ablation[C] = {"acc": round(float(accuracy_score(yh, pa.tolist())), 3),
                       "macroF1": round(float(f1_score(yh, pa.tolist(), average="macro",
                                                       zero_division=0)), 3)}
        print(f"ablation C={C}: acc={ablation[C]['acc']:.3f} "
              f"macroF1={ablation[C]['macroF1']:.3f}")

    # OOF predictions: argmax over logits must use the head's own class order.
    oof_pred_check = np.asarray(oof_classes)[oof_logits.argmax(axis=1)].tolist()
    assert oof_pred_check == oof_pred.tolist(), "OOF class-order mismatch"
    y_codes = np.asarray([oof_classes.index(v) for v in yh], dtype=int)
    temp = sh.fit_temperature(oof_logits, y_codes)
    from src.setfit_head import _softmax
    oof_proba = _softmax(oof_logits / temp)
    # temp-scaling is monotonic per-row: argmax unchanged; keep aligned OOF preds
    oof_pred_scaled = oof_pred.tolist()

    acc_oof = accuracy_score(yh, oof_pred_scaled)
    mac_oof = f1_score(yh, oof_pred_scaled, average="macro", zero_division=0)
    ci_acc = _bootstrap_ci(yh, oof_pred_scaled,
                           lambda a, b: accuracy_score(a, b))
    ci_mac = _bootstrap_ci(yh, oof_pred_scaled,
                           lambda a, b: f1_score(a, b, average="macro", zero_division=0))
    print(f"\nOOF (temp-scaled, T={temp}): acc={acc_oof:.3f} 95%CI{ci_acc} | "
          f"macroF1={mac_oof:.3f} 95%CI{ci_mac}")
    mean_mac = float(np.mean([r["macroF1"] for r in fold_rows]))
    print(f"mean per-fold macroF1={mean_mac:.3f}")

    # 5. coverage curves on scaled OOF
    msp = sh.confidence_scores(oof_proba, mode="msp")
    ene = sh.confidence_scores(oof_proba, logits=oof_logits,
                               temperature=temp, mode="energy")
    cov_msp = sh.coverage_curve(yh, oof_pred_scaled, msp)
    cov_ene_raw = sh.coverage_curve(yh, oof_pred_scaled, ene,
                                    grid=tuple(sorted(set([round(float(v), 3) for v in
                                                             np.quantile(ene, [0.0, 0.2, 0.4, 0.6, 0.8])]))))
    c90_msp = sh.coverage_at_accuracy(yh, oof_pred_scaled, msp, 0.90)
    c90_ene = sh.coverage_at_accuracy(yh, oof_pred_scaled, ene, 0.90)
    print("coverage curve (MSP):")
    for r in cov_msp:
        print(f"  conf>={r['min_conf']:.2f}: coverage={r['coverage']:.3f} "
              f"sel_acc={r['selective_acc']} n={r['n']}")
    print(f"coverage@90% MSP={c90_msp} Energy={c90_ene}")

    # per-intent OOF F1 (for the report's baseline table)
    from sklearn.metrics import precision_recall_fscore_support
    _, _, f1s, sup = precision_recall_fscore_support(yh, oof_pred_scaled,
                                                     labels=INTENTS, zero_division=0)
    per_intent = {l: {"f1": round(float(f), 3), "n": int(s)}
                  for l, f, s in zip(INTENTS, f1s, sup)}

    # baseline numbers, read-only (never rewritten)
    base = pd.read_csv(BASELINE_CSV).set_index("system")
    fin_row = base.iloc[2]
    print(f"\nTF-IDF baseline (final, human-200, read-only): "
          f"acc={fin_row['intent_acc']:.3f} macroF1={fin_row['intent_macroF1']:.3f}")
    print(f"challenger OOF delta macroF1={mac_oof - float(fin_row['intent_macroF1']):+.3f} "
          f"(OOF-vs-resubstitution caveat: baseline is resubstitution on its "
          f"weak-train distribution, challenger is OOF on human — not apples-to-apples)")

    # 6. final head on all 200 + artifact
    head_final = sh.finetune_from(head_weak, Xh, yh)
    meta = {"weak_n": len(df), "weak_pretrain_rows": len(sel),
            "human_n": len(yh), "cv_folds": sh.CV_FOLDS, "seed": sh.SEED,
            "fold_rows": fold_rows,
            "weak_head_only_acc": round(float(hw_acc), 3),
            "weak_head_only_macroF1": round(float(hw_mac), 3),
            "ablation_C": ablation,
            "oof_acc": round(float(acc_oof), 3), "oof_acc_ci95": list(ci_acc),
            "oof_macroF1": round(float(mac_oof), 3), "oof_macroF1_ci95": list(ci_mac),
            "mean_fold_macroF1": round(mean_mac, 3),
            "coverage_msp": cov_msp, "coverage_energy_quantiles": cov_ene_raw,
            "coverage_at_90_msp": c90_msp, "coverage_at_90_energy": c90_ene,
            "per_intent_oof_f1": per_intent,
            "baseline_final_acc": round(float(fin_row["intent_acc"]), 3),
            "baseline_final_macroF1": round(float(fin_row["intent_macroF1"]), 3),
            "train_seconds": round(time.perf_counter() - t_all, 1)}
    sh.save_artifact(OUT_DIR, head_final, head_weak, temp, meta)
    oof_df = pd.DataFrame({"text": texts, "human_intent": yh,
                           "oof_pred": oof_pred_scaled,
                           "oof_msp": np.round(msp, 4)})
    oof_df.to_csv(OUT_DIR / "cv_oof_preds.csv", index=False)
    print(f"\nwrote {OUT_DIR}/ (head_final.joblib, head_weak.joblib, "
          f"labels.json, meta.json, cv_oof_preds.csv)")
    print(f"CV macro-F1 mean={mean_mac:.3f} OOF={mac_oof:.3f} 95%CI{ci_mac} "
          f"(headline comparison: TF-IDF resubstitution macroF1 "
          f"{float(fin_row['intent_macroF1']):.3f})")


if __name__ == "__main__":
    sys.exit(main())
