# Cross-locus comparisons

## Tension 1: Forensics first — the leakage finding unlicenses every other locus's numbers

- **Leakage-split locus** commits: random tweet-level stratified sampling is insufficient; golden must be conversation-disjoint AND temporally posterior with retrieval-corpus exclusion. Workspace forensics: golden provenance untraceable, 200/200 golden texts verbatim in the train pool, same-thread target-in-KB unauditable — current numbers are upper bounds, not deployment estimates.
- **All other loci** commit: quantitative gates and deltas (hybrid justified at ≥5pt identifier-stratum Recall@10; SetFit within ~2% of LLM; judge weighted-κ ≥0.60-0.70; escalation AURC comparisons).
- **The cross-locus dynamic:** Every number the other five loci quote or require is *conditional on the leakage locus being fixed first*. Retrieval ablations, classifier A/Bs, and judge agreements run on thread-sprayed splits measure interpolation, not trust. This is a sequencing constraint, not a disagreement: the draft must present the split rebuild as Phase 0 and mark every pre-rebuild number an upper bound.
- **How the draft should engage this:** The data-foundation section must open with the forensic verdict and the exact split recipe before any architecture claim; the headline-critique section re-states it as the top misleading-number mechanism.
- **Calibration:** leakage investigator high on disjointness/exclusion, medium-high on temporal cutoff; all other investigators name brand-data ablations as mind-changers — consistent, since those ablations only mean anything post-rebuild.

## Tension 2: MaxProb floor vs learned routers — independent convergence on the same contest

- **SetFit-routing locus** commits: MC-dropout (M=10) routing to LLM, but MaxProb + temperature scaling is the mandatory baseline because Varshney-2022 shows nothing consistently beats MaxProb across tasks/settings.
- **Escalation locus** commits: temperature-scaled MaxProb ANDed with an NLI grounding gate as the floor; a learned confidence+difficulty calibrator admitted only on cross-split AURC + refinement wins.
- **The cross-locus dynamic:** Two investigators reached the same verdict from different directions (intent-routing economics vs escalation risk-coverage): the floor is scaled MaxProb, challengers must beat it on AURC across IID *and* temporal splits. Convergence from independent paths — the draft can assert this strongly. The shared open question is identical too: which uncertainty signal wins on brand data.
- **How the draft should engage this:** Present ONE unified confidence doctrine (scaled MaxProb floor → challenger contest on AURC → locked threshold on calibration split) serving both routing and escalation, rather than two separate mechanisms.
- **Calibration:** both 0.7-0.72; both flip on the same evidence (challenger AURC wins across splits). Genuine open question to flag, with the contest procedure pre-registered.

## Tension 3: Taxonomy size squeezed from both ends — model behavior and annotation math agree

- **SetFit-routing locus** commits: 6-10 distinct intents + explicit OOS; LLM OOS-AUCROC collapses faster than encoders as scope/label-count grow; Banking77-77 is a counter-model.
- **Golden-gate locus** commits: n=200 with ≥20/intent minimums forces ≤8-10 intents (200/20 = 10 absolute ceiling; 60-80 escalate + difficulty + temporal strata push it to ~7).
- **The cross-locus dynamic:** Model-side evidence (OOS collapse, close-intent synthetic bleed, prompt-length failures) and annotation-side arithmetic (per-label CI width at n=200) independently squeeze the taxonomy to 6-8 intents. The draft should present this as over-determined, not a judgment call — with the >15% cross-confusion merge rule as the enforcement mechanism.
- **How the draft should engage this:** The taxonomy section must show both squeezes and the merge rule; brand selection should prefer brands whose issue space compresses to ~7 distinguishable intents.
- **Calibration:** 0.72 / 0.75; both revisable on brand-data confusion matrices — the draft names the exact measurement that would change the count.

## Tension 4: Two kappa bars that must be tiered, not averaged — gold 0.80 vs judge 0.60-0.70

- **Caged-judge locus** commits: human-human interval-α ≥0.70 per dimension first, then judge-human weighted-κ ≥0.60/dimension, escalation κ ≥0.65.
- **Golden-gate locus** commits: SHIP only at Krippendorff nominal α ≥0.80 (CI lower bound ≥0.70) for intent; 0.667-0.80 tentative, <0.667 blocking.
- **The cross-locus dynamic:** Apparent conflict (0.70 vs 0.80) resolves as tiering: 0.80 certifies the *gold artifact itself* (nominal intent labels as ground truth), 0.70/0.60-0.65 govern *noisier ordinal quality dimensions and model-human agreement*. The draft must explain why different bars apply (reliability of ground truth vs fidelity of an automated rater) rather than quoting one number. Sarcasm-stratum carve-out (reported separately) is shared.
- **How the draft should engage this:** One agreement section with a tiered gate table, jackknife CIs for alpha at n=200 (bootstrap under-dispersed) alongside bootstrap elsewhere, and the explicit rule that judge certification runs only after human-human gates pass.
- **Calibration:** high on architecture, medium on exact gates (both investigators say so) — the draft frames gates as risk-calibrated choices with CIs, not theorems.

## Post-critic confidence update (Step 8)

Adversarial gap-fill (~18 new notes, 118-note corpus, 0 retracted) found no overturning source for any committed position: all six positions hold with qualifications. Changes: (a) SetFit-routing becomes conditional — full-layer MC-dropout required, Twitter-pretrained backbone required, single-pass MaxProb stays the cost default; (b) golden-gate CI method switches from bootstrap to analytical jackknife at n=200 (Hughes-2022), gate numbers hold, n=200 validated (Zapf-2016); (c) escalation primary metric becomes AUGRC (Traub-2024) with AURC retained for comparability; ACI noted as streaming extension; (d) harness build-vs-buy downgraded to contested — Langfuse CI/CD parity is real, draft must justify code-first explicitly; (e) brand choice now measurable via per-brand EDA (Amazon 169.8k tweets/11.47min median vs Apple 106.9k/70.97min vs TMobileHelp 2.75min); (f) hybrid exact-term lift quantified (+8-15%), pgvector-SQL recipe in hand, doc-only SPLADE as simplification path.

## Tension 5: The retrieval measurement plan depends on the other loci's artifacts

- **Hybrid-retrieval locus** commits: hybrid justified iff ≥5pt identifier-stratum Recall@10 gain; ablation needs identifier/paraphrase strata, conversation-disjoint temporal splits, same-thread exclusion, per-stage latency.
- **Leakage locus** commits: the split recipe that makes that ablation valid. **Golden locus** commits: the 120/80 random/hard strata including identifier-heavy tweets that supply the identifier stratum.
- **The cross-locus dynamic:** The retrieval design is the most *dependent* position: it consumes the leakage locus's splits and the golden locus's strata, and its NLI/entailment-adjacent groundedness delta feeds the escalation locus's grounding gate (π_NLImin=0.9) and the judge locus's D1 groundedness dimension. The draft must show this dependency chain explicitly — it is the systems-integration argument that the submission is one coherent harness, not six parts.
- **How the draft should engage this:** Architecture section draws the dependency graph (splits → strata → ablation → gates); complexity costs (two indices, rerank latency) are justified only through the pre-registered gate, with the in-process (rank_bm25 + FAISS/Chroma, no ES/Docker) deployment keeping reproducibility intact.
- **Calibration:** 7.5/10 highest in the set (mechanism + BEIR + three controlled deltas); only magnitudes are brand-specific — the draft states the reversal conditions verbatim.
