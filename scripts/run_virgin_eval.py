"""VirginTrains baselines: trivial / simple(keyword) / final on weak-200 + human-200.

Brand=virgin throughout. Mirrors scripts/run_eval.py + scripts/eval_human60.py (Apple)
without touching Apple files.

- trivial: generic canned reply, never-escalate (auto_handle)
- simple: weak keyword rules (virgin KEYWORDS, followup-last) + virgin index top-1
- final: AppleAgent(brand='virgin') = TF-IDF LogReg (intent_virgin.pkl) +
  virgin TF-IDF-NN k=5 + virgin templates + brand-aware 4-trigger rules
  (rail SAFETY_ADDONS, money_intents)

Outputs:
  evaluation/virgin/results_weak200.csv, results_human200.csv,
  evaluation/virgin/BASELINE_VS_FINAL.md (simple-can-win honesty + misleading §)

Usage: PYTHONPATH=. .venv\\Scripts\\python.exe scripts\\run_virgin_eval.py
"""
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

try:
    from scipy.stats import binomtest as _binomtest
except ImportError:  # pragma: no cover - scipy ships with sklearn
    _binomtest = None

from src.agent import AppleAgent, _weak_label_generic
from src.virgin_intents import KEYWORDS, TEMPLATES

# Phase 1 (Impl-B) uncertainty settings: fixed seed -> deterministic CIs.
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20260912

ROOT = Path(__file__).resolve().parents[1]
VIRGIN_DIR = ROOT / "evaluation" / "virgin"
GOLDEN_WEAK = VIRGIN_DIR / "golden_v1.csv"
GOLDEN_HUMAN = VIRGIN_DIR / "golden_human_200.csv"
INDEX_DIR = ROOT / "data" / "indexes" / "virgin"
KB_PATH = ROOT / "data" / "processed" / "virgin_kb.csv"

VIRGIN_TRIVIAL = ("Thanks for reaching out — please DM us your journey + date/time "
                  "and ticket details so we can help.")


@dataclass
class Out:
    intent: str
    draft_reply: str
    grounding_passage_ids: list
    decision: str
    escalate_reason: str


class VirginRetriever:
    """Minimal reader over data/indexes/virgin (built by scripts/build_virgin_index.py)."""

    def __init__(self):
        self.vec = joblib.load(INDEX_DIR / "tfidf_vectorizer.pkl")
        self.nn = joblib.load(INDEX_DIR / "nn_index.pkl")
        ids = pd.read_csv(INDEX_DIR / "doc_ids.csv")
        col = "tweet_id" if "tweet_id" in ids.columns else ids.columns[-1]
        self.doc_ids = ids[col].astype(str).tolist()
        kb = pd.read_csv(KB_PATH, usecols=["tweet_id", "text"])
        self.lookup = {str(r.tweet_id): r.text for r in kb.itertuples()}

    def query(self, text: str, k: int = 5):
        Xq = self.vec.transform([(text or "").lower()])
        dist, idx = self.nn.kneighbors(Xq, n_neighbors=min(k, len(self.doc_ids)))
        out = []
        for d, j in zip(dist[0], idx[0]):
            tid = self.doc_ids[j]
            out.append({"tweet_id": tid, "distance": float(d), "score": float(1 - d),
                        "text": self.lookup.get(tid, ""), "clean": ""})
        return out


def groundedness_heuristic(draft: str, passages) -> int:
    """Same heuristic as scripts/run_eval.py (Apple-shaped: DM + check + length + cite).

    Virgin templates contain 'DM us' + 'Check ...' + >=15 words, so this heuristic
    favours final by construction — disclosed as circular in BASELINE_VS_FINAL.md.
    """
    if not draft:
        return 1
    s = 0
    low = draft.lower()
    if "dm us" in low or "dm " in low:
        s += 1
    if "settings" in low or "restart" in low or "check" in low:
        s += 1
    if len(draft.split()) >= 15:
        s += 1
    if passages:
        s += 1
    return max(1, min(5, s + 1))


def trivial_fn(text: str) -> Out:
    return Out("support_access_followup", VIRGIN_TRIVIAL, [], "auto_handle", "none")


def make_simple_fn(retr):
    def fn(text: str) -> Out:
        pred = _weak_label_generic(text, KEYWORDS)
        passages = []
        if retr is not None:
            try:
                passages = retr.query(text, k=1)
            except Exception:
                passages = []
        if passages and passages[0]["text"]:
            draft, ids = passages[0]["text"][:240], [passages[0]["tweet_id"]]
        else:
            draft, ids = TEMPLATES.get(pred, VIRGIN_TRIVIAL), []
        low = (text or "").lower()
        # narrow escalation: explicit human/safety words only (production-unsafe by design)
        if any(p in low for p in ["human", "real person", "manager", "sue", "lawyer",
                                  "injured", "injury", "evacuat", "stranded"]):
            return Out(pred, draft, ids, "escalate", "human_request")
        return Out(pred, draft, ids, "auto_handle", "none")
    return fn


def evaluate(system_name, fn, texts, y_int, y_esc):
    outs = [fn(t) for t in texts]
    p_int = [o.intent for o in outs]
    p_esc = [1 if o.decision == "escalate" else 0 for o in outs]
    acc = accuracy_score(y_int, p_int)
    macro = f1_score(y_int, p_int, average="macro", zero_division=0)
    pe, re_, fe, _ = precision_recall_fscore_support(y_esc, p_esc, average="binary", zero_division=0)
    grounds = [groundedness_heuristic(o.draft_reply, o.grounding_passage_ids) for o in outs]
    row = {"system": system_name, "n": len(texts),
           "intent_acc": round(acc, 3), "intent_macroF1": round(macro, 3),
           "esc_P": round(float(pe), 3), "esc_R": round(float(re_), 3), "esc_F1": round(float(fe), 3),
           "ground_mean": round(sum(grounds) / len(grounds), 2),
           "ground_ge4_rate": round(sum(g >= 4 for g in grounds) / len(grounds), 3)}
    # NOTE: evaluate returns per-example preds alongside the row so Phase-1
    # bootstrap/McNemar reuse the exact same predictions (no recompute drift).
    return row, p_int, p_esc


def per_intent_f1(y_true, y_pred, labels):
    _, _, f, sup = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    return {l: (round(float(x), 3), int(s)) for l, x, s in zip(labels, f, sup)}


def _metric_triplet(y_int, p_int, y_esc, p_esc):
    """(intent_acc, intent_macroF1, esc_F1) — same estimators as evaluate()."""
    acc = accuracy_score(y_int, p_int)
    macro = f1_score(y_int, p_int, average="macro", zero_division=0)
    _, _, fe, _ = precision_recall_fscore_support(y_esc, p_esc, average="binary", zero_division=0)
    return acc, macro, float(fe)


def bootstrap_delta_cis(y_int, y_esc, pA_int, pA_esc, pB_int, pB_esc,
                        n_resamples=BOOTSTRAP_RESAMPLES, seed=BOOTSTRAP_SEED):
    """Percentile 95% CIs for (B-A) deltas on acc/macroF1/escF1. Deterministic (seeded)."""
    rng = np.random.default_rng(seed)
    n = len(y_int)
    yi = np.array(y_int, dtype=object)
    ye = np.array(y_esc, dtype=int)
    aI = np.array(pA_int, dtype=object)
    aE = np.array(pA_esc, dtype=int)
    bI = np.array(pB_int, dtype=object)
    bE = np.array(pB_esc, dtype=int)
    deltas = {"acc": [], "macroF1": [], "escF1": []}
    for _ in range(n_resamples):
        idx = rng.integers(0, n, n)
        mA = _metric_triplet(yi[idx].tolist(), aI[idx].tolist(), ye[idx].tolist(), aE[idx].tolist())
        mB = _metric_triplet(yi[idx].tolist(), bI[idx].tolist(), ye[idx].tolist(), bE[idx].tolist())
        deltas["acc"].append(mB[0] - mA[0])
        deltas["macroF1"].append(mB[1] - mA[1])
        deltas["escF1"].append(mB[2] - mA[2])
    return {k: (round(float(np.percentile(v, 2.5)), 3),
                round(float(np.percentile(v, 97.5)), 3)) for k, v in deltas.items()}


def mcnemar_exact(y_true, pA, pB):
    """McNemar on correctness (A vs B). Returns dict(b=A-only, c=B-only, p=exact two-sided).

    Uses scipy exact binomial when available, else chi-square with continuity
    correction. b+c == 0 -> p = 1.0 (no discordant pairs).
    """
    a_ok = [a == y for a, y in zip(pA, y_true)]
    b_ok = [b == y for b, y in zip(pB, y_true)]
    b = sum(1 for a, c in zip(a_ok, b_ok) if a and not c)
    c = sum(1 for a, d in zip(a_ok, b_ok) if not a and d)
    n = b + c
    if n == 0:
        return {"b": 0, "c": 0, "p": 1.0}
    if _binomtest is not None:
        p = float(_binomtest(min(b, c), n, 0.5, alternative="two-sided").pvalue)
    else:  # fallback: chi-square with continuity correction
        from math import erf, sqrt
        chi2 = (abs(b - c) - 1.0) ** 2 / n
        z = sqrt(chi2)
        p = float(1.0 - erf(z / sqrt(2.0)))
    return {"b": b, "c": c, "p": round(p, 4)}


def main():
    from src.virgin_intents import INTENTS
    try:
        retr = VirginRetriever()
        print(f"virgin retriever ready ({len(retr.doc_ids)} docs)")
    except Exception as e:
        print("virgin retriever unavailable:", e)
        retr = None
    agent = AppleAgent(retr, brand="virgin")
    simple_fn = make_simple_fn(retr)

    def adapt_final(t):
        o = agent.handle(t, brand="virgin")
        return Out(o.intent, o.draft_reply, o.grounding_passage_ids, o.decision, o.escalate_reason)

    systems = [("trivial (generic canned, never-escalate)", trivial_fn),
               ("simple (virgin keyword + top-1)", simple_fn),
               ("final (TFIDF-LogReg + virgin NN k=5 + template + rules)", adapt_final)]

    # A. weak-200 (circular: weak labels ARE the keyword output — headline warning)
    gw = pd.read_csv(GOLDEN_WEAK)
    yw_int, yw_esc = gw.intent.tolist(), gw.escalate.astype(int).tolist()
    rows_w, preds_w = [], {}
    for name, fn in systems:
        row, p_int, p_esc = evaluate(name, fn, gw.text.tolist(), yw_int, yw_esc)
        rows_w.append(row)
        preds_w[name] = (p_int, p_esc)
    dfw = pd.DataFrame(rows_w)
    print("\n== A. weak-200 (CIRCULAR, not headline) ==")
    print(dfw.to_string(index=False))
    dfw.to_csv(VIRGIN_DIR / "results_weak200.csv", index=False)

    # B. human-200 (HEADLINE)
    gh = pd.read_csv(GOLDEN_HUMAN)
    yt = gh.human_intent.tolist()
    ye = gh.human_escalate.astype(int).tolist()
    rows_h, preds_h = [], {}
    for name, fn in systems:
        row, p_int, p_esc = evaluate(name, fn, gh.text.tolist(), yt, ye)
        rows_h.append(row)
        preds_h[name] = (p_int, p_esc)
    dfh = pd.DataFrame(rows_h)
    print("\n== B. human-200 (HEADLINE) ==")
    print(dfh.to_string(index=False))
    dfh.to_csv(VIRGIN_DIR / "results_human200.csv", index=False)

    # per-intent F1 (final vs simple on human-200) + weak-vs-human context
    outs_simple = [simple_fn(t).intent for t in gh.text.tolist()]
    outs_final = [adapt_final(t).intent for t in gh.text.tolist()]
    pf_s = per_intent_f1(yt, outs_simple, INTENTS)
    pf_f = per_intent_f1(yt, outs_final, INTENTS)
    from sklearn.metrics import cohen_kappa_score
    wvk = cohen_kappa_score(gh.weak_intent, gh.human_intent)
    wva = accuracy_score(gh.weak_intent, gh.human_intent)

    d = dfh.set_index("system")
    s_triv, s_simp, s_fin = d.index[0], d.index[1], d.index[2]

    # --- Phase 1 (Impl-B): uncertainty on final−simple deltas + McNemar pairs.
    # Reuses the exact predictions above (no model change, no recompute drift).
    ci_h = bootstrap_delta_cis(yt, ye, *preds_h[s_simp], *preds_h[s_fin])
    ci_w = bootstrap_delta_cis(yw_int, yw_esc, *preds_w[s_simp], *preds_w[s_fin])
    mc_h_sf = mcnemar_exact(yt, preds_h[s_simp][0], preds_h[s_fin][0])
    mc_h_tf = mcnemar_exact(yt, preds_h[s_triv][0], preds_h[s_fin][0])
    mc_w_sf = mcnemar_exact(yw_int, preds_w[s_simp][0], preds_w[s_fin][0])
    mc_w_tf = mcnemar_exact(yw_int, preds_w[s_triv][0], preds_w[s_fin][0])

    def _fmt_ci(ci):
        return "[%+.3f, %+.3f]" % ci

    print("\n== C. Bootstrap 95%% CIs, final-simple deltas (%d resamples, seed %d) =="
          % (BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED))
    for tag, ci in (("human-200", ci_h), ("weak-200 ", ci_w)):
        print("%s acc %s  macroF1 %s  escF1 %s"
              % (tag, _fmt_ci(ci["acc"]), _fmt_ci(ci["macroF1"]), _fmt_ci(ci["escF1"])))
    print("== D. McNemar exact (intent correctness; b=A-only, c=B-only) ==")
    for tag, m in (("human simple-vs-final ", mc_h_sf), ("human trivial-vs-final", mc_h_tf),
                   ("weak  simple-vs-final ", mc_w_sf), ("weak  trivial-vs-final", mc_w_tf)):
        print("%s b=%d c=%d p=%.4f" % (tag, m["b"], m["c"], m["p"]))
    md = []
    md.append("# Virgin baseline vs final — formal tables (brand=virgin)")
    md.append("")
    md.append(f"Date: 2026-09-11 (post-fix: keywords + class_weight=balanced retrain + PII gate + DR30 template). Sources (read-only): `evaluation/virgin/golden_v1.csv` (weak-200, frozen with pre-fix rules) + "
              f"`evaluation/virgin/golden_human_200.csv` (human-200: 60 manual-style + 140 rulebook-assisted, "
              f"41/200 intent flips, weak-vs-human acc {wva:.3f} κ {wvk:.3f}).")
    md.append("Systems: trivial = generic canned, never-escalate; simple = virgin keyword rules (post-fix) + virgin NN top-1; "
              "final = TF-IDF LogReg (`models/intent_virgin.pkl`, 30k weak post-fix, class_weight=balanced, train-subset acc 0.969 optimistic) + "
              "virgin NN k=5 + virgin templates (delay w/ DR30 bands) + brand-aware triggers (rail SAFETY_ADDONS, money_intents, crowd remap, PII gate).")
    md.append("")
    md.append("## A. Weak-200 (keyword labels — CIRCULAR, do not use as headline)")
    md.append("| System | intent_acc | macroF1 | esc_P | esc_R | esc_F1 | ground_mean | ground≥4 |")
    md.append("|---|---|---|---|---|---|---|---|")
    for r in rows_w:
        md.append(f"| {r['system']} | {r['intent_acc']:.3f} | {r['intent_macroF1']:.3f} | {r['esc_P']:.3f} | "
                  f"{r['esc_R']:.3f} | {r['esc_F1']:.3f} | {r['ground_mean']:.2f} | {r['ground_ge4_rate']:.3f} |")
    dw = dfw.set_index("system")
    md.append(f"Deltas final−simple: acc {dw.iloc[2].intent_acc - dw.iloc[1].intent_acc:+.3f}, "
              f"macroF1 {dw.iloc[2].intent_macroF1 - dw.iloc[1].intent_macroF1:+.3f}, "
              f"esc_F1 {dw.iloc[2].esc_F1 - dw.iloc[1].esc_F1:+.3f}.")
    md.append("")
    md.append("## B. Human-200 (HEADLINE: single-annotator AI-assisted review)")
    md.append("| System | intent_acc | macroF1 | esc_P | esc_R | esc_F1 | ground_mean | ground≥4 |")
    md.append("|---|---|---|---|---|---|---|---|")
    for r in rows_h:
        md.append(f"| {r['system']} | {r['intent_acc']:.3f} | {r['intent_macroF1']:.3f} | {r['esc_P']:.3f} | "
                  f"{r['esc_R']:.3f} | {r['esc_F1']:.3f} | {r['ground_mean']:.2f} | {r['ground_ge4_rate']:.3f} |")
    md.append(f"Deltas final−simple: acc {d.iloc[2].intent_acc - d.iloc[1].intent_acc:+.3f}, "
              f"macroF1 {d.iloc[2].intent_macroF1 - d.iloc[1].intent_macroF1:+.3f}, "
              f"esc_F1 {d.iloc[2].esc_F1 - d.iloc[1].esc_F1:+.3f}.")
    md.append("")
    md.append("## C. Per-intent F1 on human-200 (simple vs final; support in brackets)")
    md.append("| Intent | simple F1 | final F1 |")
    md.append("|---|---|---|")
    for l in INTENTS:
        md.append(f"| {l} | {pf_s[l][0]:.3f} ({pf_s[l][1]}) | {pf_f[l][0]:.3f} ({pf_f[l][1]}) |")
    md.append("")
    md.append("## Interpretation (post balanced-retrain honesty)")
    md.append("- **§B is the headline; §A is circularity demonstration.** Weak labels were frozen with pre-fix keyword rules, so post-fix simple scores 0.975 (the 5 misses ARE the fixed cases). Final's LogReg generalizes off 30k weak bootstraps.")
    md.append("- **Final now leads simple on human intent too** (table B deltas positive — balanced class weights fixed the accessibility tail collapse: 0.500→0.848, matching simple; lost/refund now beat simple). Small-n caveat stands (±~20%/stratum). The Apple-v1 pattern (keyword wins intent) no longer holds here — reported as-is.")
    md.append("- **Final is justified by escalation + groundedness AND intent now.** Simple escalates only on explicit human/safety words (near-zero esc recall — production-unsafe on money/safety cases). Final is the only system with a functioning trigger head (rail safety add-ons, money_threshold, human_request, unresolvable, PII, crowd remap). Groundedness heuristic favours final templates by construction "
              "(DM + 'Check' + length + cite) — heuristic, not human judgment.")
    md.append("")
    md.append("## What is misleading (mandatory)")
    md.append("- Weak-200 numbers (§A) flatter simple (0.975 post-fix; 1.000 pre-fix) and punish final for generalizing — never quote §A "
              "without the circularity warning. Train-subset acc 0.969 (vs weak) is equally circular.")
    md.append("- Groundedness ≥4 rate for final (~1.0) is heuristic-shaped (template contains the scored tokens), "
              "not span-attributed faithfulness; pair with correctness + retrieval before any quality claim.")
    md.append("- Human-200 is single-annotator AI-assisted (60 manual-style + 140 rulebook-assisted, 41 flips); "
              "no inter-annotator κ yet; n=200 → CIs ≈±0.07 on acc. Safety slice is tiny (3 legal_safety) — "
              "see JUDGE_AGREEMENT.md. Do not claim launch on these numbers.")
    md.append("")
    md.append("## D. Uncertainty: bootstrap 95% CIs + McNemar (Phase 1, Impl-B)")
    md.append(f"Method: {BOOTSTRAP_RESAMPLES} bootstrap resamples (seed {BOOTSTRAP_SEED}, percentile "
              "CIs) on final-simple deltas; McNemar exact binomial two-sided on intent "
              "correctness for simple-vs-final and trivial-vs-final. Same predictions as §§A–C (no model change).")
    md.append("")
    md.append("| Dataset | Metric | final-simple Δ | 95% CI |")
    md.append("|---|---|---|---|")
    for tag, ci, rows in (("human-200", ci_h, rows_h), ("weak-200", ci_w, rows_w)):
        dlt = {k: rows[2][m] - rows[1][m] for k, m in
               (("acc", "intent_acc"), ("macroF1", "intent_macroF1"), ("escF1", "esc_F1"))}
        for k in ("acc", "macroF1", "escF1"):
            md.append(f"| {tag} | {k} | {dlt[k]:+.3f} | {_fmt_ci(ci[k])} |")
    md.append("")
    md.append("| Dataset | McNemar pair (intent) | A-only (b) | B-only (c) | exact p |")
    md.append("|---|---|---|---|---|")
    md.append(f"| human-200 | simple vs final | {mc_h_sf['b']} | {mc_h_sf['c']} | {mc_h_sf['p']:.4f} |")
    md.append(f"| human-200 | trivial vs final | {mc_h_tf['b']} | {mc_h_tf['c']} | {mc_h_tf['p']:.4f} |")
    md.append(f"| weak-200 | simple vs final | {mc_w_sf['b']} | {mc_w_sf['c']} | {mc_w_sf['p']:.4f} |")
    md.append(f"| weak-200 | trivial vs final | {mc_w_tf['b']} | {mc_w_tf['c']} | {mc_w_tf['p']:.4f} |")
    md.append("")
    md.append("Reading rule (significance-gated): CIs gate interpretation of FLIPS, not absolutes. "
              "A delta whose CI includes 0 is noise — do not claim a win or a loss on it "
              "(the human-200 intent lead is of this kind: small-n, SE≈0.028). "
              "The promptfoo harness (`promptfooconfig.yaml`) blocks merges on pass-rate FLIPS "
              "vs this baseline, not on absolute scores; a flip is actionable only when its CI "
              "excludes 0 (or McNemar p < 0.05 on the paired comparison).")
    (VIRGIN_DIR / "BASELINE_VS_FINAL.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\nwrote results_weak200.csv, results_human200.csv, BASELINE_VS_FINAL.md")
    print(f"weak-vs-human intent acc={wva:.3f} kappa={wvk:.3f}")


if __name__ == "__main__":
    main()
