# Annotation + LLM-Judge Run Protocol (keyless state, 2026-09-11)

Status: heuristic judge only (no `GROQ_API_KEY` / `OPENAI_API_KEY` in env).
LLM path is implemented + fail-closed verified (`groq_smoke.py` no-key → 5/5 template).
This doc is the exact procedure to finish the "proof" once a key exists. Nothing here is claimed as done.

## 1. Second annotator (inter-annotator κ, currently missing)

- Sample: `evaluation/virgin/spotcheck_30.csv` (30, already human-labelled by annotator 1)
  + 20 fresh draws from `data/processed/virgin_inbound_pool.csv` (seed 11, exclude golden IDs) → n=50.
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

## 2. LLM-judge run (blocked on key)

- With key: `$env:GROQ_API_KEY="gsk_..."; $env:PYTHONPATH="C:\Hiver";
  C:\Hiver\.venv\Scripts\python.exe C:\Hiver\scripts\groq_smoke.py` (expect 5/5 groq path),
  then run judge hook on the 50-item set above (rubric `evaluation/rubric.md`,
  model pinned `gpt-4o-mini-2026-07-01`, temp 0, double-run for self-consistency).
- Report: per-dimension weighted κ + PASS/FAIL Cohen κ + safety-FAIL recall.
- Ship gate (unchanged): groundedness wκ ≥ 0.60 AND safety-recall ≥ 0.90, else advisory-only.
- Cost guard: never bulk LLM on critical path; free tier ~30 RPM; template is default.

## 3. Mined-slice supporting evidence (done keyless, 2026-09-11)

- `scripts/mine_safety_slice.py` (seed 9): safety regex-mined n=20 → system escalation rate **1.000**;
  money regex-mined n=40 → **0.575**. Raw slice: `evaluation/virgin/safety_slice.csv`.
- Honesty: these are NOT human-labelled recall — they measure trigger coverage on lexicon-mined
  candidates (money slice includes non-escalatable mentions like "save me money").
  Human-labelled recall stays: safety 1.000 (n=3, tiny) + money 0.800 (n=20).
