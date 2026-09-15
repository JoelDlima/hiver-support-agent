"""Virgin judge agreement: heuristic judge vs human labels on golden_human_200.

Mirrors scripts/run_judge_agreement.py (Apple) for brand=virgin without touching
Apple files. Heuristic judge runs offline; LLM hook stays no-key (logged honestly).

Reports:
- safety recall: human legal_safety cases -> system escalated (ship gate >=0.90)
- money recall: human money_threshold cases -> system escalated
- escalation vs human: acc / Cohen kappa / P / R / F1
- groundedness distribution (heuristic, circular-by-design — disclosed)

Writes evaluation/virgin/judge_scores_200.csv + evaluation/virgin/JUDGE_AGREEMENT.md

Usage: PYTHONPATH=C:\\Hiver C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\run_virgin_judge.py
"""
import pandas as pd
from pathlib import Path
from sklearn.metrics import cohen_kappa_score, accuracy_score, precision_recall_fscore_support

from run_virgin_eval import VirginRetriever
from src.agent import AppleAgent
from evaluation.judge import heuristic_judge, llm_judge, RUBRIC_VERSION

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "evaluation" / "virgin" / "golden_human_200.csv"
OUT_CSV = ROOT / "evaluation" / "virgin" / "judge_scores_200.csv"
OUT_MD = ROOT / "evaluation" / "virgin" / "JUDGE_AGREEMENT.md"


def main():
    df = pd.read_csv(GOLD)
    try:
        retr = VirginRetriever()
    except Exception as e:
        print("virgin retriever unavailable:", e)
        retr = None
    agent = AppleAgent(retr, brand="virgin")
    rows = []
    for r in df.itertuples():
        o = agent.handle(r.text, brand="virgin")
        trending = ([{"text": "kb"} for _ in o.grounding_passage_ids]
                    if o.grounding_passage_ids else [{"text": ""}])
        js = heuristic_judge(o.intent, o.draft_reply, trending, r.text)
        lj, note = llm_judge(o.intent, o.draft_reply, o.grounding_passage_ids, r.text)
        rows.append({"text": r.text, "human_intent": r.human_intent, "pred_intent": o.intent,
                     "human_esc": int(r.human_escalate), "pred_esc": 1 if o.decision == "escalate" else 0,
                     "human_reason": r.human_reason, "pred_reason": o.escalate_reason,
                     "ground": js.groundedness, "safety_j": js.safety, "verdict": js.verdict,
                     "llm": note})
    res = pd.DataFrame(rows)
    res.to_csv(OUT_CSV, index=False)

    saf = res[res.human_reason == "legal_safety"]
    srec = float((saf.pred_esc == 1).mean()) if len(saf) else float("nan")
    mon = res[res.human_reason == "money_threshold"]
    mrec = float((mon.pred_esc == 1).mean()) if len(mon) else float("nan")
    acc = accuracy_score(res.human_esc, res.pred_esc)
    try:
        kap = cohen_kappa_score(res.human_esc, res.pred_esc)
    except Exception:
        kap = float("nan")
    p, rr, f, _ = precision_recall_fscore_support(res.human_esc, res.pred_esc, average="binary", zero_division=0)
    print(f"n={len(res)} safety_cases={len(saf)} safety_recall={srec:.3f}" if len(saf) else "no safety cases")
    print(f"money_cases={len(mon)} money_recall={mrec:.3f}" if len(mon) else "no money cases")
    print(f"esc acc={acc:.3f} kappa={kap:.3f} P={p:.3f} R={rr:.3f} F1={f:.3f}")
    print(f"ground mean={res.ground.mean():.2f} >=4 rate={(res.ground >= 4).mean():.3f} "
          f"verdict PASS={(res.verdict == 'PASS').mean():.3f}")
    print(f"llm note: {res.llm.iloc[0]} rubric={RUBRIC_VERSION}")

    lines = [
        f"# Virgin judge agreement ({RUBRIC_VERSION}, brand=virgin)",
        "",
        f"- n={len(res)} (golden_human_200), heuristic judge offline; LLM hook: {res.llm.iloc[0]}",
        f"- Safety: {len(saf)} human legal_safety cases, system escalate recall={srec:.3f} (ship gate >=0.90). "
        f"n={len(saf)} is tiny — CI spans ~0.4–1.0; gate NOT claimable on this slice alone.",
        f"- Money: {len(mon)} human money_threshold cases, system escalate recall={mrec:.3f}.",
        f"- Escalation vs human: acc={acc:.3f} kappa={kap:.3f} P={p:.3f} R={rr:.3f} F1={f:.3f}",
        f"- Groundedness: mean={res.ground.mean():.2f}, >=4 rate={(res.ground >= 4).mean():.3f}, "
        f"PASS={(res.verdict == 'PASS').mean():.3f} (heuristic, template-shaped — circular by design)",
        f"- Weak-vs-human context: intent acc 0.795 κ 0.772 (41/200 flips; see build_virgin_golden.py adjudication notes)",
        "- Gate: groundedness wκ>=0.60 + safety-recall>=0.90 to ship LLM judge; currently heuristic advisory-only.",
        f"- Prompt: evaluation/judge.py JUDGE_PROMPT (temp 0, pinned model gpt-4o-mini-2026-07-01); double-run recommended.",
        "",
        "## What is misleading (mandatory)",
        "- Heuristic groundedness ≈1.0 PASS flatters template drafts (scored tokens are IN the template). "
        "It measures template-shape, not span-attributed faithfulness. Never report as reply quality.",
        f"- Safety recall on n={len(saf)} cannot pass a >=0.90 ship gate with confidence; report the count, "
        "not just the rate. Money recall (n=20) is the better-powered escalation signal here.",
        "- LLM judge: keyed n=30 study in evaluation/virgin/LLM_JUDGE_30.md (qwen temp 0: verdict κ=0.253, wκ=0.060 → gate holds, advisory-only).",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_CSV} + {OUT_MD}")


if __name__ == "__main__":
    main()
