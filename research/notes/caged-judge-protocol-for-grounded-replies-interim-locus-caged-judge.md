---
title: Caged judge protocol for grounded replies (interim, locus caged-judge)
id: caged-judge-protocol-for-grounded-replies-interim-locus-caged-judge
tags:
- hiver-support-agent-audit-6d951f
- locus-caged-judge-protocol-for-grounded-replies
created: '2026-09-15T02:39:22.329420Z'
status: draft
type: interim
deprecated: false
summary: Anchored pointwise CoT+rubric judge, cross-family separation, agreement gates;
  RAGAS secondary
---

# Caged-Judge Protocol for Grounded Support Replies — Depth Investigation (locus: caged-judge-protocol-for-grounded-replies)

## Locus and verdict under investigation

Which rubric + mitigation + human-anchor bundle makes an LLM judge trustworthy for three distinct
objects — **groundedness** (reply entailed by retrieved brand history), **resolution-usefulness**
(would this plausibly resolve/advance the issue per brand playbook), and **escalation-appropriateness**
(auto-handle vs escalate + reason)? Sub-question: can RAGAS reference-free scores headline, or stay secondary?

## What the width corpus actually says (full-text reading, not summaries)

### 1. The bias inventory is settled science; the mechanisms point at structural (not prompt-only) fixes

- Three headline biases recur across every source: **position** (slot preference), **verbosity**
  (longer wins regardless of content), **self-preference/self-enhancement** (own-family outputs scored
  higher). Two further skews matter for support replies: **style/format bias** (markdown/structure rewarded
  independent of content) and **sycophancy** (confident/authoritative tone rewarded over accurate hedging).
  Sources: [[llm-judge-biases-position-verbosity-self-preference-aitldr]],
  [[llm-as-a-judge-pitfalls-bias-detection-mitigation-aitldr]].
- **Position mechanism**: sequential attention asymmetry (primacy/recency; lost-in-the-middle family).
  Older work: swap consistency only 70.5–77.3% (~1 verdict in 4 flips on order alone), code-eval accuracy
  shifts >10pp on swap. **Caveat that changes the design**: the newest controlled study (5 judges, 4 families,
  375 controlled pairs) finds position bias now **negligible (≤0.04)** on current-generation models — likely
  instruction-tuning progress — while **style bias dominates at 0.10–0.76** across models (Pro +0.76,
  Flash +0.72, Claude +0.68, Llama +0.40; GPT-4o near-neutral +0.10), confirmed as bias not readability by a
  human-annotation check (humans prefer markdown 57%; judges 73–97%).
  Sources: [[judging-the-judges-a-systematic-evaluation-of-bias-mitigation-strategies-in-llm]],
  [[why-llm-judges-are-biased-position-self-preference]].
- **Self-preference mechanism**: not ego but **perplexity familiarity** — judges over-rate low-perplexity
  (easy-to-predict) text whether or not they wrote it; own outputs are low-perplexity by construction.
  Quantified by an equal-opportunity-based metric: GPT-4 bias **0.52** (recall gap 0.945 vs 0.425), highest of
  8 models; demographic-parity variant 0.749 for GPT-4. Prompt instruction alone does not remove it.
  The clean methodological advance is the **DBG score** (EMNLP 2025): bias = judge score on own outputs
  **minus gold judgments** as quality proxy, which disentangles "judge likes its own style" from "judge's
  outputs are genuinely better" — the naive own-vs-other score difference conflates the two.
  Sources: [[self-preference-bias-in-llm-as-a-judge]],
  [[beyond-the-surface-measuring-self-preference-in-llm-judgments-acl-anthology]].
- **Verbosity is heterogeneous, not uniform** (length-aware measurement): Llama/Pro/Flash show classical
  verbosity bias (+0.24 to +0.44 for longer on expansion pairs); Claude prefers concise (−0.12); GPT-4o
  neutral (−0.04). All models correctly prefer genuinely complete answers on truncation pairs (0.88–1.00).
  Implication: never assume a fixed verbosity direction — **measure it per judge**.
  Source: [[judging-the-judges-a-systematic-evaluation-of-bias-mitigation-strategies-in-llm]].
- Sycophancy fix with the best evidence: **require cited textual evidence before the score** + rubric language
  penalizing unsupported confidence ("incorrect-confident < correct-hedged").
  Source: [[llm-as-a-judge-pitfalls-bias-detection-mitigation-aitldr]].

### 2. What actually moves judge–human agreement (controlled numbers, MT-Bench n=400, bootstrap CIs ±~0.05)

- Strongest configuration: **merged CoT + calibrated rubric in one prompt, verdict as a separate JSON field,
  called with position swap (S8 "Combined Budget")** — Flash 71.0% (κ=0.549, p<0.0001, ~$0.001/eval);
  Claude +11.5pp, Flash +7.5pp, Llama +4.5pp (all significant; Claude/Flash survive Holm-Bonferroni over 20
  comparisons). **CoT alone (S5)** is the safest default: universally non-negative, best on adversarial
  LLMBar (Claude +13.0pp), and the most consistent style-bias reducer (Pro 0.76→0.60, Claude 0.68→0.49).
  The merged prompt also lowers swap-disagreement tie rates (Claude ties 32.8%→12.5%) because stronger
  prompts produce more order-consistent verdicts.
- **Position swap is double-edged**: helps tie-resolution on natural data (Flash +4.7pp) but **hurts
  −3 to −13pp on adversarial/clear-cut items** (3 Holm-Bonferroni-significant negatives) by discarding
  correct verdicts as ties. Rule: swap-aggregate only for close-call system comparison, never for grading
  clear-cut gold items.
- G-Eval (full method read): auto-generated evaluation steps (CoT) + **form-filling paradigm** + verdict,
  with **probability-weighted continuous scoring** (score = Σ p(sᵢ)·sᵢ; sample n=20 at temp 1 when token
  probs unavailable) beats discrete-only scoring on Spearman (GPT-4: ρ=0.514 avg summarization; Topical-Chat
  avg ρ=0.588; QAGS avg ρ=0.611). CoT ablation: 0.514 vs 0.500 without. G-Eval itself documents the
  pro-LLM tilt: it scores GPT summaries above human ones **even where humans prefer the human ones**, on a
  slice where human–human Krippendorff α was 0.07 — i.e. judge bias is loudest exactly where humans disagree.
  Sources: [[judging-the-judges-a-systematic-evaluation-of-bias-mitigation-strategies-in-llm]],
  [[g-eval-nlg-evaluation-using-gpt-4-with-better-human-alignment]].

### 3. Verbosity control has a canonical statistical fix

- Length-controlled AlpacaEval (GLM: predict auto-annotator preference from length difference + covariates,
  then counterfactualize at zero length difference) is robust to verbosity gaming and lifts Chatbot Arena
  Spearman **0.94→0.98**. Rubric anti-verbosity clauses help but are imperfect alone; the regression is the
  load-bearing control for any pairwise win-rate headline.
  Source: [[length-controlled-alpacaevala-simple-way-to-debias-automatic-evaluators]].

### 4. Agreement machinery and task-calibrated targets

- Metric→use mapping: **Cohen κ** = two raters, categorical (escalation decision, pairwise wins);
  **quadratic-weighted κ** = ordinal 1–5 dimensions (large errors penalized more; equals ICC under stated
  assumptions); **Fleiss κ** = multi-rater pilot with interchangeable raters; **Krippendorff α** = production
  (any rater count, missing data via coincidence matrices, nominal/ordinal/interval distance functions —
  choose interval for Likert, nominal for escalation; wrong choice inflates/deflates); **Spearman/Kendall**
  = continuous/ranked scores (Kendall τ on discrete scores inflates via ties — use probability-weighted
  continuous scores); Bradley–Terry for preference aggregation.
- Targets must be task-calibrated, not Landis–Koch worship (0.61–0.80 "substantial" is medical, not NLP):
  objective ≥0.90; **moderately subjective (our reply-quality case) 0.70–0.85**; inherently subjective
  preference 0.60–0.75 (sarcasm/Twitter-tone work legitimately <0.35). Production floor in the judge
  literature: **75% judge–human agreement, 80% swap consistency**; re-audit monthly and on any judge/rubric
  change. Report bands with bootstrap 95% CIs (±0.05 at n=400 → **±0.06–0.10 at our n=150–250**); never
  4-decimal precision. Under class imbalance report **per-class** agreement (the escalate minority class is
  where the signal lives). Operate IAA continuously: 5–15% overlap, rolling windows, critique reviews of
  reasoning (labels can agree for different reasons), adjudication into gold.
  Sources: [[inter-annotator-agreement-for-llm-evaluation-guide]],
  [[cohen-fleiss-krippendorff-iaa-metrics-implementation-interactive]].

### 5. RAGAS reference-free scores: the sub-question is settled against headlining

- RAGAS Faithfulness = claim-extraction → per-claim entailment check vs retrieved context → supported/total
  (0–1); implemented with an LLM (or the HHEM-2.1 T5 classifier for the entailment step).
  Source: [[faithfulness-ragas]].
- Three independent strikes against headlining: (i) Deutsch et al. (EMNLP 2022): reference-free metrics are
  **formally one generation model evaluating another** — test-time optimizable, biased toward self-similar
  models, **biased against higher-quality/human outputs** — recommendation: **diagnostic tools, never
  progress measures**; (ii) G-Eval's own pro-LLM tilt (above); (iii) every RAGAS LLM-based score inherits
  the full bias inventory (position/verbosity/self/style) with no human anchor.
  Source: [[on-the-limitations-of-reference-free-evaluations-of-generated-text-acl-anthology]].
- Legitimate RAGAS roles: unsupervised retrieval-health signal, low-faithfulness triage flag for human
  review, drift monitor — preferably the **non-LLM HHEM entailment variant** to break judge-on-judge
  circularity, each spot-checked against humans.

## Design consequences for the Hiver golden set (150–250) and harness

- **Pointwise anchored scoring is the primary instrument** (kills position bias by construction — the right
  move now that position ≤0.04 but style dominates); reserve pairwise double-swap strictly for
  baseline-vs-candidate comparison on close calls, with tie-on-disagreement and swap-consistency reporting.
- Three scored dimensions + one classification (escalation is a decision, not a Likert item — a graded
  deliverable per the assignment: decision + reason).
- Human–human agreement gates the gold before any judge number is quoted; judge–human agreement gates the
  judge before any headline is quoted; RAGAS runs unanchored in the appendix/diagnostics.
- n=150–250 implies wide CIs and MDE ≈6–8pp: the report's "misleading headline" section writes itself —
  any sub-6pp system gap at this n is noise, and every metric needs its CI printed beside it.

## Committed position

**SIDE: adopt the "anchored pointwise CoT+rubric judge with cross-family separation and statistical length
control" as the single headline instrument.** Exact cage: (1) Rubric = three 1–5 anchored dimensions —
**D1 Groundedness** (every actionable claim entailed by cited retrieved brand context; unsupported claim =
cap at 2), **D2 Resolution-usefulness** (correct next step/channel per brand playbook; generic deflection
caps at 3), **D3 Safety-honesty** (no invented policy/compensation/timeline, no PII echo, uncertainty
qualified) — each with **few-shot 1/3/5 anchors** (fixes scale drift) plus a separate **E: escalate?
{auto-handle | escalate + reason}** categorical verdict scored as classification, never Likert; verdict
emitted as its own JSON field, never summed from criteria. (2) Prompt = G-Eval form-filling + merged
CoT+rubric (S8-style) at temperature 0.1 with **evidence-citation-before-score** (anti-sycophancy),
explicit **anti-verbosity and anti-format clauses** ("concise-correct > wordy-partial; content only, ignore
markdown/tone"), formatting normalized pre-judge, graded content wrapped in XML as untrusted
(prompt-injection guard); probability-weighted continuous scores where logprobs exist (else discrete + tie
rate reported). (3) **Judge model family MUST differ from every generator family** under test (self-preference
is perplexity-structural: GPT-4 bias 0.52/DP 0.749; no prompt fully removes it); default to the empirically
safest profile — CoT-forcing judge with neutrality on verbosity (GPT-4o-like) or quality-sensitive concise
profile — and verify per-judge. (4) Agreement gates, all with bootstrap 95% CIs: human–human first
(≥20% double-annotated overlap; Krippendorff interval-α ≥0.70 per dimension, Cohen κ ≥0.70 on E) before gold
is certified; then judge–human promotion bar — **quadratic-weighted κ ≥0.60 per dimension, Cohen κ ≥0.65 on
E, raw agreement ≥75%, pairwise-arm swap consistency ≥0.80, |length–score Spearman| <0.15, DBG-style
self-preference gap <0.10**; system comparisons by McNemar/mixed-effects logistic with Holm-Bonferroni and a
pre-registered MDE (~6–8pp at n=200); any pairwise win-rate headline additionally passes length-controlled
GLM (AlpacaEval-LC style). (5) Disagreement analysis = stratified confusion (dimension × intent × action
type) + per-class κ on the escalate minority + critique review of 20–30 mismatches classified as
guideline-gap / judge-bias / genuine-ambiguity feeding back into anchors, with 100–300-pair held-out
calibration set re-audited on schedule (drop <75% → re-prompt/rotate). (6) **RAGAS stays secondary**:
Faithfulness (+answer-relevancy) reported only as diagnostic/triage signals, preferably via the non-LLM
HHEM entailment step, each spot-checked vs humans — because reference-free scores are one model grading
another (test-time optimizable, self-similarity-biased, at times anti-human: Deutsch et al. 2022; G-Eval
tilt at human α=0.07), so they can monitor and flag but never headline. Confidence: **high** on the cage
architecture (convergent controlled experiments across 4+ families); **medium** on exact numeric gates
(task- and n-specific, CIs wide at 150–250). What would change my mind: (a) our calibration at n≥200 shows
pairwise swap-aggregated judging beating anchored pointwise on judge–human weighted-κ with CIs excluding
zero; (b) style-mirrored pairs + length–score audit showing ≈0 format/length effects without controls;
(c) same-family judge with DBG gap ≈0 across intents; (d) RAGAS-faithfulness reaching weighted-κ ≥0.70 vs
human groundedness on our gold — which would promote it to co-headline.
