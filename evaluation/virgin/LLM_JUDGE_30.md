# LLM-as-Judge Agreement Study — Virgin spotcheck_30 (n=30, 2026-09-11)

First keyed LLM-judge run. Key via `GROQ_API_KEY` env only (never in code/logs/outputs — verified by grep).

## Setup
- Items: `evaluation/virgin/spotcheck_30.csv` (human intent/escalate labels pre-existing).
- Drafts: current final agent (`AppleAgent` + retrained `intent_virgin.pkl` + templates) → `llm_judge_30_drafts.csv` (0 LLM calls).
- Human grades: single annotator (operator) blind to LLM scores — `human_grades_30.csv`
  (groundedness 1–5 + strict QA verdict PASS/FAIL; 19 PASS / 11 FAIL).
  FAIL = wrong-intent draft, unsafe/dismissive reply, or false receipt claim. Templates make almost
  no falsifiable claims, so human groundedness sits at 3–4 for 29/30 — relevance carries the verdict.
- LLM judge: Groq `qwen/qwen3.8-27b`, temp 0, rubric prompt (`run_llm_judge_30.py` JUDGE_SYSTEM),
  JSON-as-hint + server-side validate, paced 2.5s (free-tier guard). 30/30 scored → `llm_judge_30_scores.csv`.
  NOTE: model is NOT the pinned `gpt-4o-mini-2026-07-01` (`llama-3.3-70b-versatile` is retired —
  `NotFoundError` on first attempt). Scores are not transferable across judge models.
- Script: `scripts/run_llm_judge_30.py --drafts / --judge / --agree` (re-runnable; `--judge` needs key).

## Results
- Verdict agreement: 19/30 raw (0.633), **Cohen κ = 0.253 (fair)**.
- Groundedness: human 3–4 almost everywhere vs LLM 1–5 spread → **quadratic wκ = 0.060 (~chance)**.
- PASS rates: human 0.633, LLM 0.533, heuristic 1.000 (heuristic never FAILs → κ ≈ 0.000 vs human).
- Confusion (LLM rows × human cols): LLM-PASS/human-PASS 12, LLM-PASS/human-FAIL 4 (idx 0,1,8,13 —
  LLM gave ground 4–5 to wrong-intent drafts), LLM-FAIL/human-PASS 7 (idx 11,21,22,25,27,28,29 —
  LLM failed correct drafts with ground=2), LLM-FAIL/human-FAIL 7.

## Reading
1. LLM judge beats the heuristic (κ 0.253 vs ~0.000) but **fails our own ship gate
   (groundedness wκ ≥ 0.60) → stays ADVISORY**. Shipped claim: none. This is the gate working as designed.
2. Calibration split: the LLM conflates relevance with groundedness (wrong-intent → ground 1–2;
   sometimes ground 5 for equally wrong drafts, idx 0/1). Humans separate them (ground 4, verdict FAIL).
   Groundedness-as-scored cannot separate good from bad template drafts — verdict must come from
   relevance + escalation correctness.
3. The rubric formula (`overall ≥ 3.5 → PASS`) lets wrong-intent drafts pass arithmetically
   (0.35·4+0.25·3+0.15·3+0.15·5+0.10·2 = 3.55). Strict QA overrides it. Follow-ups attempted same-day:
   (a) adding `relevance ≤ 2 → FAIL` to the *heuristic* verdict — REVERTED, it keys on
   other-predictions so it FAILed reasonable triage while PASSing confident wrong-intent drafts
   (heur-vs-human κ=-0.297 on this 30, worse than the ungated ~0.000); relevance gating needs a
   genuinely graded relevance signal, not the other-prediction proxy.
   (b) applying the same gate to the *LLM* verdicts offline — REDUNDANT here (0/30 verdicts change:
   every LLM rel≤2 item already failed via groundedness≤2; κ stays 0.253). Rubric text updated to
   state the gate; heuristic code deliberately unchanged.
4. Limits: n=30 single-annotator both sides (my grades + one LLM temp-0 run, no self-consistency
   double-run yet); qwen ≠ pinned OpenAI judge; passages column was empty in the judge call
   (retrieval IDs existed but texts unpassed — span-attribution untested).

## Next (needs key + time)
- Re-run with `relevance ≤ 2 → FAIL` gate + pass retrieved passage texts (span faithfulness).
- Double-run LLM for self-consistency; second human annotator for the 30 (see `docs/ANNOTATION_PROTOCOL.md`).
- Then re-evaluate the wκ ≥ 0.60 gate.

## Follow-up v2 + Groq A/B (keyed, same day — Temp script `ab_v2.py`, outputs committed)

- **Judge v2** (passage texts top-3 passed + double-run): self-consistency **1.000** (30/30 identical,
  temp-0 deterministic) but verdict κ **-0.005**, raw 0.533 — WORSE than v1 (κ=0.253). Passages made the
  judge lenient on wrong-intent drafts (ground 5 / rel 4–5 justifying misdirected templates) and harsh on
  correct ones (7 correct drafts failed). Deterministic ≠ valid: reliably miscalibrated both runs.
  → `llm_judge_30_v2.csv`. Gate holds (advisory-only) for the second time, now with evidence that
  "add passages" is not the fix — relevance grading itself is broken.
- **Groq draft A/B** (same 30, keyed agent = groq-first fail-closed): **29/30 groq path** (1 `too-long`
  rejection → template), mean served length 218 chars, all ≤280. → `groq_ab_30.csv`. Qualitative: groq
  drafts add one concrete next step (e.g. National Rail app check, peak/off-peak explanation) but inherit
  intent errors identically (same classifier) — upgrade in specificity, not direction. No superiority claim;
  template remains the default, groq behind validation gate.
- **Annotation pack for annotator 2**: `annotation_pack_50.csv` (30 spotcheck + 20 fresh seed-11) +
  `scripts/build_annotation_pack.py`, per `docs/ANNOTATION_PROTOCOL.md` §1. The single biggest trust
  upgrade left is human, not technical.

## Groq-vs-template judged comparison (same judge, same rubric, n=30)

- Method: the 29 live groq drafts + 1 template fallback from `groq_ab_30.csv`, judged by the same
  qwen temp-0 rubric → `groq_judge_30.csv`, compared against template-draft scores.
- Means — groundedness 3.00 vs 3.13 (−0.13, noise), actionability 3.73 vs 3.60 (+0.13, directionally
  as hypothesized but tiny), voice 4.70 vs 4.73 (tie), safety 5.00 vs 5.00 (tie),
  **relevance 3.90 vs 3.17 (+0.73 — the one real signal: groq drafts answer the specific ask,
  templates deflect to generic triage)**, verdict PASS 0.500 vs 0.533 (tie).
- Caveats (blocking any superiority claim): same-model grading (qwen judges qwen — self-preference
  risk per literature), n=30 single-run, template path remains default. Verdict: groq stays an
  opt-in specificity upgrade behind the validation gate, not a replacement.
