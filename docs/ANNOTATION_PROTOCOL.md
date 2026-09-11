# Annotation + LLM-Judge Run Protocol (keyed n=30 study done 2026-09-11)

Status 2026-09-11: first keyed run complete — Groq `qwen/qwen3.8-27b`, temp 0, n=30 spotcheck
(`evaluation/virgin/LLM_JUDGE_30.md`): verdict κ=0.253 (fair), groundedness wκ=0.060 →
gate holds, advisory-only. Key via `GROQ_API_KEY` env only (never in code/logs/outputs — verified by grep).
LLM path is implemented + fail-closed verified (`groq_smoke.py` keyed → 5/5 groq path).
This doc is the exact procedure to finish the "proof" once a key exists. Nothing here is claimed as done.

## 1. Second annotator (inter-annotator κ — PACK READY, needs a human)

- Pack: `evaluation/virgin/annotation_pack_50.csv` (built by `scripts/build_annotation_pack.py`:
  30 spotcheck_30 with annotator-1 labels stripped to empty columns + 20 fresh draws seed-11
  excluding golden/spotcheck texts). Annotator 2 fills `human_intent` / `human_escalate` / `human_reason`.
- Schema per item: `human_intent` (10 Virgin intents), `human_escalate` (0/1), `human_reason`
  (legal_safety | money_threshold | money_review | human_request | unresolvable | complaint_review | none).
- Adjudication: disagreements resolved by rulebook (`src/virgin_intents.py` DESCRIPTIONS + money/safety
  lexicons); log flips like the 41-flip log for golden-200.
- Command: `$env:PYTHONPATH="C:\Hiver"; C:\Hiver\.venv\Scripts\python.exe -c
  "import pandas as pd; from sklearn.metrics import cohen_kappa_score;
  a=pd.read_csv('annotator1.csv'); b=pd.read_csv('annotator2.csv');
  print('intent κ=', round(cohen_kappa_score(a.human_intent,b.human_intent),3));
  print('esc κ=', round(cohen_kappa_score(a.human_escalate,b.human_escalate),3))"`
- Ship bar: intent κ ≥ 0.60 AND esc κ ≥ 0.60; else revise rulebook, not the metrics.

## 2. LLM-judge run (first keyed run DONE 2026-09-11 — see `evaluation/virgin/LLM_JUDGE_30.md`)

- Ran: `$env:GROQ_API_KEY` (env only) + `scripts/run_llm_judge_30.py --drafts / --judge / --agree`
  on spotcheck_30 (30/30 scored, qwen/qwen3.8-27b temp 0, paced 2.5s). Re-runnable any time a key is set.
- Re-run after: `relevance ≤ 2 → FAIL` gate fix + passing retrieved passage texts (span faithfulness).
- Report: per-dimension weighted κ + PASS/FAIL Cohen κ + safety-FAIL recall.
- Ship gate (unchanged): groundedness wκ ≥ 0.60 AND safety-recall ≥ 0.90, else advisory-only.
- Cost guard: never bulk LLM on critical path; free tier ~30 RPM; template is default.

## 3. Mined-slice supporting evidence (done keyless, 2026-09-11)

- `scripts/mine_safety_slice.py` (seed 9): safety regex-mined n=20 → system escalation rate **1.000**;
  money regex-mined n=40 → **0.575**. Raw slice: `evaluation/virgin/safety_slice.csv`.
- Honesty: these are NOT human-labelled recall — they measure trigger coverage on lexicon-mined
  candidates (money slice includes non-escalatable mentions like "save me money").
  Human-labelled recall stays: safety 1.000 (n=3, tiny) + money 0.800 (n=20).
