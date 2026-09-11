"""Evaluation harness: intent, escalation, retrieval, reply-judge (heuristic, offline) + agreement stub."""
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support, confusion_matrix, cohen_kappa_score
from src.agent import AppleAgent, trivial_baseline, keyword_baseline
from src.retriever import Retriever

GOLDEN = Path(r"C:\Hiver\evaluation\golden_v1.csv")

def groundedness_heuristic(draft: str, passages) -> int:
    """1-5 heuristic: template replies with DM + diagnostic step score 4; canned 3; empty 1."""
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

def run_system(fn, texts, k_retrieval_check=None):
    outs = [fn(t) for t in texts]
    return outs

def evaluate(system_name, fn, golden: pd.DataFrame, retriever=None):
    texts = golden.text.tolist()
    y_int = golden.intent.tolist()
    y_esc = golden.escalate.astype(int).tolist()
    outs = run_system(fn, texts)
    p_int = [o.intent for o in outs]
    p_esc = [1 if o.decision == "escalate" else 0 for o in outs]
    acc = accuracy_score(y_int, p_int)
    macro = f1_score(y_int, p_int, average="macro", zero_division=0)
    pe, re_, fe, _ = precision_recall_fscore_support(y_esc, p_esc, average="binary", zero_division=0)
    # retrieval recall@k proxy: does top-1 passage exist (always true if retriever) — report coverage + score
    scores = []
    grounds = []
    for o in outs:
        grounds.append(groundedness_heuristic(o.draft_reply, o.grounding_passage_ids))
    return {
        "system": system_name,
        "n": len(golden),
        "intent_acc": round(acc, 3),
        "intent_macroF1": round(macro, 3),
        "esc_P": round(float(pe), 3), "esc_R": round(float(re_), 3), "esc_F1": round(float(fe), 3),
        "ground_mean": round(sum(grounds) / len(grounds), 2),
        "ground_ge4_rate": round(sum(g >= 4 for g in grounds) / len(grounds), 3),
    }

def main():
    golden = pd.read_csv(GOLDEN)
    try:
        retr = Retriever()
    except Exception as e:
        print("retriever unavailable:", e)
        retr = None
    agent = AppleAgent(retr, brand="apple")  # Apple golden: pin brand (default is virgin primary)
    rows = []
    rows.append(evaluate("trivial (majority+canned, never-escalate→auto)", trivial_baseline, golden))
    rows.append(evaluate("simple (keyword + BM25 top-1)", lambda t: keyword_baseline(t, retr), golden))
    rows.append(evaluate("final (TFIDF-LogReg + TFIDF-NN + template + rules)", agent.handle, golden))
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    df.to_csv(Path(r"C:\Hiver\evaluation\results.csv"), index=False)
    print("\nvs-baselines deltas (final - simple):")
    print(f"  intent_acc {df.iloc[2].intent_acc - df.iloc[1].intent_acc:+.3f}, macroF1 {df.iloc[2].intent_macroF1 - df.iloc[1].intent_macroF1:+.3f}, esc_F1 {df.iloc[2].esc_F1 - df.iloc[1].esc_F1:+.3f}")
    print("\nNOTE: golden labels are weak-label drafts (see build_golden). Headline numbers are optimistic vs true human labels — see 'What is misleading' in report.")

if __name__ == "__main__":
    main()
