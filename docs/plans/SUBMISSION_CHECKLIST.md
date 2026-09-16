# Hiver Submission Checklist — 7 PS deliverables (all inside `.`)

Date: 2026-09-11. Brand: **VirginTrains primary** (27,817 outbound / 37,444 inbound), AppleSupport kept as transfer proof. Rule: headline = human-200, never weak-200 (circular).

| # | PS deliverable | Status | Path(s) |
|---|---|---|---|
| 1 | Working system (classify → retrieve → draft → escalate; API + demo, Groq fail-closed) | DONE | `src/agent.py`, `src/brands.py`, `src/virgin_intents.py`, `src/groq_draft.py`, `backend/main.py` (`/predict` brand-aware, `/metrics`), `frontend/app.py` (Virgin default), `models/intent_virgin.pkl`, `data/indexes/virgin/` |
| 2 | 6-page Virgin report (6 sections: framing/not-built, baselines weak+human, top-5 failures w/ real examples, misleading, next week incl. Groq, decisions pointer + Apple transfer row) | DONE | `docs/REPORT_VIRGIN_6PAGE.md` (human-200 headline: final 0.795/0.803, esc 0.778/0.757/0.767; Apple human-60/human-200 transfer rows; re-verified 2026-09-11 balanced-retrain) |
| 3 | README + repro (headline block: brand, volumes, intents, golden 200, intent/esc numbers, safety recall, baselines, judge gate, repro 2.3 min) | DONE | `README.md` (Virgin headline block + quickstart; Apple transfer block kept); repro: `scripts/build_virgin_kb.py`, `scripts/build_virgin_index.py`, `pytest tests -q`, `docs/REPRO_CHECK.md` |
| 4 | Decision log (15 Apple + Virgin addenda: brand-agnostic, Groq-behind-gate, safety add-ons, money escalation, keyword fixes, PII/DR30/balanced, LLM-study + reverted gate) | DONE | `docs/DECISION_LOG.md` (31 entries; pointer in report §6) |
| 5 | Baselines vs final (trivial/simple/final on weak-200 circular + human-200 headline + per-intent; deltas + honesty note) | DONE | `evaluation/virgin/BASELINE_VS_FINAL.md` (§A weak / §B human / §C per-intent), `evaluation/virgin/results_weak200.csv`, `evaluation/virgin/results_human200.csv`, `evaluation/virgin/SAMPLING_NOTE.md`, `evaluation/virgin/golden_v1.csv`, `evaluation/virgin/golden_human_200.csv` |
| 6 | Judge agreement + safety gate (heuristic offline; LLM hook gated wκ ≥0.60 + safety-recall ≥0.90; safety n=3 + money n=20 reported) | DONE (keyed n=30: v1 κ 0.253, v2 κ -0.005 self-consist 1.000 → gate holds twice, advisory-only) | `evaluation/virgin/JUDGE_AGREEMENT.md`, `evaluation/virgin/LLM_JUDGE_30.md`, `evaluation/judge.py`, `scripts/run_llm_judge_30.py` |
| 7 | Failure tests (real pool probes, PASS/PARTIAL/FAIL verdicts + hypotheses H1–H7, no unsafe output) | DONE (9/9 PASS, re-probe 2026-09-11 balanced-retrain + `tests/test_virgin_fixes.py` 7 probes) | `evaluation/virgin/FAILURE_TESTS.md` (F1 DR30 done, F2 fixed, F3 PII pii_review done, F4/F5/F6/F7 fixed) |

## Reviewer notes (from websearch: repro checklist, judge-κ, decision-log standards)

- Repro (Pineau/REFORMS): deps in `requirements.txt`, seeds 7/11/42, exact commands in README, data in `data/raw/` + `data/processed/`, expected artifacts listed per command, runtime + hardware disclosed (dev-CPU; virgin index 0.5s/p50 7.1ms; Apple pipeline 2.3 min).
- Judge: report chance-corrected κ (esc-vs-human κ 0.715; weak-vs-human κ 0.772) + P/R + n + confusion source, never raw agreement alone; safety 1.000 (n=3) NOT a gate pass; money 0.850 (17/20) is the powered signal; mined-slice safety 1.000 (n=20) / money 0.575 (n=40) is coverage-only, not recall. LLM v1 κ 0.253 / v2 κ -0.005 (self-consist 1.000) → gate holds twice. Annotator-2 pack: `evaluation/virgin/annotation_pack_50.csv` + `docs/ANNOTATION_PROTOCOL.md`.
- Decisions: each entry = context → choice → rejected alternative → consequence → revisit trigger (ADR style); report §6 is pointer-only, full why in `docs/DECISION_LOG.md`.
- Nothing lives outside `.`. No secrets in repo (Groq via `GROQ_API_KEY` env only, fail-closed `no-key` → template).
