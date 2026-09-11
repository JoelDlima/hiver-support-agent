"""Judge-human agreement: heuristic judge vs human labels on golden_human_200 sample.
Evidence: safety recall on human legal_safety cases + groundedness distribution + kappa context.
Writes evaluation/JUDGE_AGREEMENT_V2.md + judge_scores_200.csv
"""
import pandas as pd
from pathlib import Path
from sklearn.metrics import cohen_kappa_score, accuracy_score
from src.agent import AppleAgent
from src.retriever import Retriever
from evaluation.judge import heuristic_judge, llm_judge, RUBRIC_VERSION

GOLD = Path(r"C:\Hiver\evaluation\golden_human_200.csv")

def main(n=200, seed=5):
    df = pd.read_csv(GOLD)
    retr = Retriever(); agent = AppleAgent(retr, brand="apple")  # Apple golden: pin brand (default is virgin primary)
    rows = []
    for r in df.itertuples():
        o = agent.handle(r.text)
        js = heuristic_judge(o.intent, o.draft_reply, [{"text": p["text"]} for p in [{"text": ""}]] if not o.grounding_passage_ids else [{"text": "kb"} for _ in o.grounding_passage_ids], r.text)
        lj, note = llm_judge(o.intent, o.draft_reply, o.grounding_passage_ids, r.text)
        rows.append({"text": r.text, "human_intent": r.human_intent, "pred_intent": o.intent,
                     "human_esc": int(r.human_escalate), "pred_esc": 1 if o.decision == "escalate" else 0,
                     "human_reason": r.human_reason, "pred_reason": o.escalate_reason,
                     "ground": js.groundedness, "safety_j": js.safety, "verdict": js.verdict,
                     "llm": note})
    res = pd.DataFrame(rows)
    res.to_csv(Path(r"C:\Hiver\evaluation\judge_scores_200.csv"), index=False)
    # safety recall: human legal_safety cases -> did we escalate?
    saf = res[res.human_reason == "legal_safety"]
    srec = (saf.pred_esc == 1).mean() if len(saf) else float("nan")
    # agreement: pred esc vs human esc
    from sklearn.metrics import precision_recall_fscore_support, f1_score
    acc = accuracy_score(res.human_esc, res.pred_esc)
    try:
        kap = cohen_kappa_score(res.human_esc, res.pred_esc)
    except Exception:
        kap = float("nan")
    p, r, f, _ = precision_recall_fscore_support(res.human_esc, res.pred_esc, average="binary", zero_division=0)
    print(f"n={len(res)} safety_cases={len(saf)} safety_recall={srec:.3f}" if len(saf) else "no safety cases")
    print(f"esc acc={acc:.3f} kappa={kap:.3f} P={p:.3f} R={r:.3f} F1={f:.3f}")
    print(f"ground mean={res.ground.mean():.2f} >=4 rate={(res.ground>=4).mean():.3f} verdict PASS={(res.verdict=='PASS').mean():.3f}")
    print(f"llm note: {res.llm.iloc[0]} rubric={RUBRIC_VERSION}")
    Path(r"C:\Hiver\evaluation\JUDGE_AGREEMENT_V2.md").write_text(
        f"# Judge agreement v2 ({RUBRIC_VERSION})\n\n- n={len(res)} (golden_human_200), heuristic judge offline; LLM hook: {res.llm.iloc[0]}\n"
        f"- Safety: {len(saf)} human legal_safety cases, system escalate recall={srec:.3f} (ship gate >=0.90)\n"
        f"- Escalation vs human: acc={acc:.3f} kappa={kap:.3f} P={p:.3f} R={r:.3f} F1={f:.3f}\n"
        f"- Groundedness: mean={res.ground.mean():.2f}, >=4 rate={(res.ground>=4).mean():.3f}, PASS={(res.verdict=='PASS').mean():.3f}\n"
        f"- Weak-vs-human context: intent kappa 0.465 (60-manual); esc kappa 0.015 (heuristic labels ~random)\n"
        f"- Gate: groundedness wK>=0.60 + safety-recall>=0.90 to ship LLM judge; currently heuristic advisory-only.\n"
        f"- Prompt: evaluation/judge.py JUDGE_PROMPT (temp 0, pinned model gpt-4o-mini-2026-07-01); double-run recommended.\n", encoding="utf-8")

if __name__ == "__main__":
    main()
