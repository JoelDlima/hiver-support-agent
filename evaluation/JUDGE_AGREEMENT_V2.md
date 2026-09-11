# Judge agreement v2 (judge-v1-2026-09-10)

- n=200 (golden_human_200), heuristic judge offline; LLM hook: no-key: heuristic only (set OPENAI_API_KEY for gpt-4o-mini run)
- Safety: 11 human legal_safety cases, system escalate recall=0.909 (ship gate >=0.90)
- Escalation vs human: acc=0.840 kappa=0.508 P=0.480 R=0.800 F1=0.600
- Groundedness: mean=4.83, >=4 rate=1.000, PASS=1.000
- Weak-vs-human context: intent kappa 0.465 (60-manual); esc kappa 0.015 (heuristic labels ~random)
- Gate: groundedness wK>=0.60 + safety-recall>=0.90 to ship LLM judge; currently heuristic advisory-only.
- Prompt: evaluation/judge.py JUDGE_PROMPT (temp 0, pinned model gpt-4o-mini-2026-07-01); double-run recommended.
