"""Ablation: isolate retrieval + classifier contributions on golden_human_60.

Systems:
  A final          = AppleAgent(retriever)  [TFIDF-LogReg + TFIDF-NN k=5 + template + rules]
  B no-retrieval   = AppleAgent(retriever=None) [same classifier/draft/rules, no passages]
  C keyword-only   = keyword_baseline + retriever top-1 [weak rules, no learned classifier]
  D trivial        = majority canned, never-escalates (auto_handle)

Metrics: intent acc / macroF1 (vs human_intent), esc P/R/F1 (vs human_escalate),
  grounding proxy: share with >=1 passage id (retrieval coverage), no_grounding escalate rate.
Usage: .venv\\Scripts\\python.exe scripts\\run_ablation.py
Does NOT overwrite results.csv / results_human60.csv (prints only + writes ABLATION table stdout).
"""
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

from src.agent import AppleAgent, trivial_baseline, keyword_baseline
from src.retriever import Retriever

ROOT = Path(__file__).resolve().parents[1]
HUMAN60 = ROOT / "evaluation" / "golden_human_60.csv"


def eval_system(name, fn, texts, y_int, y_esc):
    outs = [fn(t) for t in texts]
    p_int = [o.intent for o in outs]
    p_esc = [1 if o.decision == "escalate" else 0 for o in outs]
    acc = accuracy_score(y_int, p_int)
    macro = f1_score(y_int, p_int, average="macro", zero_division=0)
    p, r, f, _ = precision_recall_fscore_support(y_esc, p_esc, average="binary", zero_division=0)
    grounded = sum(1 for o in outs if o.grounding_passage_ids) / len(outs) if outs else 0.0
    no_ground_esc = sum(1 for o in outs if o.escalate_reason == "unresolvable") / len(outs) if outs else 0.0
    return {
        "system": name,
        "n": len(texts),
        "intent_acc": round(float(acc), 3),
        "intent_macroF1": round(float(macro), 3),
        "esc_P": round(float(p), 3),
        "esc_R": round(float(r), 3),
        "esc_F1": round(float(f), 3),
        "grounded_rate": round(float(grounded), 3),
        "unresolvable_rate": round(float(no_ground_esc), 3),
    }


def main():
    df = pd.read_csv(HUMAN60)
    texts = df.text.tolist()
    y_int = df.human_intent.tolist()
    y_esc = df.human_escalate.astype(int).tolist()
    try:
        retr = Retriever()
    except Exception as e:
        print("retriever unavailable:", e)
        retr = None
    agent_full = AppleAgent(retr, brand="apple")  # Apple golden: pin brand (default is virgin primary)
    agent_noret = AppleAgent(None, brand="apple")

    rows = []
    rows.append(eval_system("D trivial (majority+canned)", trivial_baseline, texts, y_int, y_esc))
    rows.append(eval_system("C keyword-only (weak rules + top-1)", lambda t: keyword_baseline(t, retr), texts, y_int, y_esc))
    rows.append(eval_system("B no-retrieval (LogReg, retriever=None)", agent_noret.handle, texts, y_int, y_esc))
    rows.append(eval_system("A final (LogReg + TFIDF-NN + rules)", agent_full.handle, texts, y_int, y_esc))
    out = pd.DataFrame(rows)
    print(out.to_string(index=False))
    print("\nDeltas vs final (final - other):")
    fin = rows[3]
    for r in rows[:3]:
        print(f"  final - {r['system'][:28]:28s} intent_acc {fin['intent_acc']-r['intent_acc']:+.3f} "
              f"macroF1 {fin['intent_macroF1']-r['intent_macroF1']:+.3f} esc_F1 {fin['esc_F1']-r['esc_F1']:+.3f} "
              f"grounded {fin['grounded_rate']-r['grounded_rate']:+.3f}")
    print("\nNOTE: n=60, single annotator; deltas have wide CIs. "
          "Retrieval effect is visible in esc/unresolvable + grounded_rate, not intent_acc "
          "(classifier identical in A vs B by design).")


if __name__ == "__main__":
    main()
