# Virgin judge agreement (judge-v1-2026-09-10, brand=virgin)

- n=200 (golden_human_200), heuristic judge offline; LLM hook: no-key: heuristic only (set OPENAI_API_KEY for gpt-4o-mini run)
- Safety: 3 human legal_safety cases, system escalate recall=1.000 (ship gate >=0.90). n=3 is tiny — CI spans ~0.4–1.0; gate NOT claimable on this slice alone.
- Money: 20 human money_threshold cases, system escalate recall=0.800.
- Escalation vs human: acc=0.855 kappa=0.577 P=0.580 R=0.784 F1=0.667
- Groundedness: mean=4.28, >=4 rate=1.000, PASS=1.000 (heuristic, template-shaped — circular by design)
- Weak-vs-human context: intent acc 0.795 κ 0.772 (41/200 flips; see build_virgin_golden.py adjudication notes)
- Gate: groundedness wκ>=0.60 + safety-recall>=0.90 to ship LLM judge; currently heuristic advisory-only.
- Prompt: evaluation/judge.py JUDGE_PROMPT (temp 0, pinned model gpt-4o-mini-2026-07-01); double-run recommended.

## What is misleading (mandatory)
- Heuristic groundedness ≈1.0 PASS flatters template drafts (scored tokens are IN the template). It measures template-shape, not span-attributed faithfulness. Never report as reply quality.
- Safety recall on n=3 cannot pass a >=0.90 ship gate with confidence; report the count, not just the rate. Money recall (n=20) is the better-powered escalation signal here.
- LLM judge unrun (no key) — zero LLM-judge scores claimed; hook verified fail-closed (no-key note logged).
