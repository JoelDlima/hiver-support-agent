# Virgin groundedness-judge agreement V3 (workstream A1)

- Agreement set: n=30 (spotcheck_30 drafts from `llm_judge_30_drafts.csv` — the exact drafts the human graded — vs `human_grades_30.csv` groundedness 1-5, single annotator blind to LLM).
- Judge: shipped `POST /judge/groundedness` (sentence claim-split + per-claim entail/passage-cite). Model leg: **heuristic-offline** (temp n/a (offline heuristic); Groq primary `openai/gpt-oss-20b`, fallback `qwen/qwen3.8-27b`).
- Mapping: fraction-supported -> 1-5 via 1+round(4*frac). Primary: quadratic-weighted Cohen k vs human 1-5.
- Result: exact=0.033, within-1=0.033, **wK=0.007 95% CI [0.0, 0.021]** (bootstrap 2000, seed 20260912).
- Gate wK>=0.6: **FAIL**.
- Distributions — human 1-5: {3: 3, 4: 27}; judge 1-5: {1: 24, 2: 5, 4: 1}.
- Coverage (context, not gate): 200/200 golden_human_200 live template drafts scored, mean fraction-supported=0.115.

## Method notes (anti-tuning)
- The entailment rule was frozen BEFORE this run on 5 ungraded pilot probes (instrument piloting, blind to human labels): stemmed content-token coverage >=1/3 in a single passage. No threshold was moved after seeing agreement numbers; no rubric edits against the 30.
- Drafts are fixed artifacts (`llm_judge_30_drafts.csv`); passages re-retrieved live (virgin NN k=5). Re-running reproduces bit-identically offline.
- Human side is single-annotator (same limitation as v1/v2); n=30 -> wide CIs. The 200-coverage run has no human labels and cannot pass any gate.

## What is misleading (mandatory)
- A low wK here does NOT mean drafts are bad: humans grade templates 3-4 for having almost no falsifiable claims ('triage acceptable'), while claim-entailment is strict about novel template wording (Delay Repay bands, DM instructions) that retrieved customer tweets rarely contain verbatim. Strict instrument vs lenient humans is the expected disagreement shape (same split v1 found for relevance vs groundedness).
- Heuristic-offline != LLM judge: the Groq semantic leg (primary when keyed) may agree better; this file reports the offline leg only until a keyed re-run exists. Do not quote this wK against the LLM path.
- n=30 single-annotator: CIs span ~0.4 wide; no launch claim is supportable from this slice alone.

## Next
- Keyed re-run (GROQ_API_KEY): same script, LLM leg answers, temp 0; compare wK + self-consistency double-run.
- Second human annotator on the 30 (double-label k); blinded relabel pack is workstream C.

## Per-item table (audit)

| idx | human_ground | judge_frac | judge_5 | n_claims | supported | human_verdict |
|---|---|---|---|---|---|---|
| 0 | 4 | 0.000 | 1 | 2 | 0 | FAIL |
| 1 | 4 | 0.000 | 1 | 2 | 0 | FAIL |
| 2 | 4 | 0.000 | 1 | 3 | 0 | FAIL |
| 3 | 4 | 0.000 | 1 | 3 | 0 | PASS |
| 4 | 4 | 0.000 | 1 | 3 | 0 | PASS |
| 5 | 4 | 0.000 | 1 | 3 | 0 | PASS |
| 6 | 3 | 0.000 | 1 | 3 | 0 | FAIL |
| 7 | 4 | 0.000 | 1 | 3 | 0 | PASS |
| 8 | 3 | 0.000 | 1 | 3 | 0 | FAIL |
| 9 | 4 | 0.000 | 1 | 3 | 0 | PASS |
| 10 | 4 | 0.000 | 1 | 3 | 0 | PASS |
| 11 | 4 | 0.000 | 1 | 2 | 0 | PASS |
| 12 | 4 | 0.000 | 1 | 2 | 0 | PASS |
| 13 | 4 | 0.000 | 1 | 2 | 0 | FAIL |
| 14 | 4 | 0.000 | 1 | 3 | 0 | PASS |
| 15 | 4 | 0.333 | 2 | 3 | 1 | PASS |
| 16 | 4 | 0.000 | 1 | 3 | 0 | PASS |
| 17 | 4 | 0.333 | 2 | 3 | 1 | FAIL |
| 18 | 4 | 0.000 | 1 | 3 | 0 | PASS |
| 19 | 4 | 0.000 | 1 | 3 | 0 | FAIL |
| 20 | 4 | 0.333 | 2 | 3 | 1 | PASS |
| 21 | 4 | 0.667 | 4 | 3 | 2 | PASS |
| 22 | 4 | 0.000 | 1 | 2 | 0 | PASS |
| 23 | 4 | 0.000 | 1 | 3 | 0 | FAIL |
| 24 | 3 | 0.000 | 1 | 3 | 0 | FAIL |
| 25 | 4 | 0.000 | 1 | 3 | 0 | PASS |
| 26 | 4 | 0.000 | 1 | 3 | 0 | FAIL |
| 27 | 4 | 0.333 | 2 | 3 | 1 | PASS |
| 28 | 4 | 0.333 | 2 | 3 | 1 | PASS |
| 29 | 4 | 0.000 | 1 | 3 | 0 | PASS |
