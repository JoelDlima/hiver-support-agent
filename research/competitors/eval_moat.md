# Eval Moat — Why Our Evaluation Is the Differentiation (Hiver, 2026-09-10)

**Brief context:** every team has the same build brief; the stated hard part is eval rigor ("proof worth more than system").
This note is the evidence that our proof layer is the moat. Method: 10 websearch queries (2026-09-10) + local artifact audit.
Scope: judge agreement, RAG faithfulness vs recall@k, escalation asymmetric risk, misleading-metric containment, failure analysis.

## 1. LLM-as-judge: agreement (kappa), not correlation

**What the literature says (2025–2026):**

1. **Correlation lies; kappa decides.** Judge's Verdict Benchmark (54 LLMs, 1,994 items, 3 annotators): 36 judges clear r≥0.80 correlation, but only 27 reach Tier-1 after kappa + human-likeness z-test. Human–human static baseline κ̄=**0.801**; Tier-1 bar = κ **0.781–0.816** with |z|<1. A judge can correlate perfectly while being systematically harsh/lenient. (arxiv 2510.09738)
2. **Kappa deflation is universal.** Largest systematic study (21 judges, 9 providers, ~541k judgments, MT-Bench/JudgeBench/RewardBench, Mar–Apr 2026): exact-match overstates Cohen's κ by **33–41pp on MT-Bench** (cohort mean 38.6pp; best judge EM 0.849 → κ 0.511). "85% agreement" ≈ κ 0.48 (moderate), not near-perfect. Headline must be the chance-corrected metric. Minimum Viable Validation Protocol: chance-correct by default, ≥2 benchmarks, consistency+bias jointly. (arxiv 2606.19544)
3. **On binary verdicts, r = ρ = τ = φ = MCC — one number, not five.** Reporting Pearson+Spearman+Kendall side-by-side manufactures triangulation from a single statistic. Cohen's κ is the one that adds information: its gap from φ measures judge↔human positive-rate drift; |κ|≤|φ|, equality iff marginal rates match. Protocol choice alone (verdict extraction × threshold × abstention rule × aggregation) moves reported accuracy **0.551→0.899** and κ across zero **without changing one verdict**. Report protocol + confusion matrix + coverage, not just the scalar. (arxiv 2606.00093)
4. **Consistency ≠ validity; biases are model-specific.** Test–retest >0.95 coexists with position bias >0.10 (Qwen3-8B 0.992/0.192, Gemini-2.5-Flash 0.988/0.125) — the consistency–bias paradox. Position flip rates 25–50% in older work; 2026 controlled pairs show position bias ≤0.04 on some rigs but **style bias 0.76–0.92 dominates**; verbosity picture is heterogeneous (Pro/Llama/Flash +0.24–+0.44 prefer-longer; Claude −0.12 concise; GPT-4o ≈neutral) — test your judge, don't assume a direction. Required mitigations: order-swapped double scoring + length control + robustness reporting; position-swap helps MT-Bench-style data but **hurts** curated adversarial sets (−3 to −13pp). Single-judge panels can amplify shared biases; bias-aware aggregation (JURY) drives pure-bias probes 0.73→~0.50. (arxiv 2604.23178; VERDICT-BENCH; CyclicJudge 2603.01865)
5. **Sample-level agreement is the real number.** 105,600-instance study: model-level Spearman ρ=0.99 masks sample-level r=0.72 and ICC=0.67; rubric structure alone restores 62% of agreement ("Evaluation Illusion"). High-quality outputs get the *least* consistent evaluations. (arxiv 2603.11027)

**What typical submissions do:** cite accuracy / exact-match / correlation (r≈0.8–0.95) as "judge validated", single run, unpinned model, no swap test, no kappa, no bias audit.

**What we do (`evaluation/JUDGE_AGREEMENT.md`, `JUDGE_AGREEMENT_V2.md`, `evaluation/judge.py`, `evaluation/rubric.md`):**
- Zero LLM-judge scores claimed. Heuristic offline judge only (deterministic, $0), distribution disclosed as **circular-by-design** (templates score 4–5 by construction): human-60 mean **4.72**, ≥4 rate 1.000; human-200 mean **4.83**, PASS 1.000.
- Pinned LLM hook ready but gated: `JUDGE_PROMPT` (judge-v1-2026-09-10), temp 0, pinned `gpt-4o-mini-2026-07-01`, JSON-schema output, double-run recommended; returns `no-key: heuristic only` without key — no faked scores (§36).
- Ship-gate frozen: groundedness weighted-κ **≥0.60 AND safety-FAIL recall ≥0.90** on the 60-overlap calibration set; heuristic held to the same bar (not yet κ-scored — stated).
- Agreement context published next to every headline: weak-vs-human intent κ **0.465** / esc κ **0.015**; final-vs-human intent κ 0.363 / esc κ 0.213 (n=60); human-200 escalation κ **0.487**. Our 0.465 sits far below the Tier-1 0.78+ band — disclosed as distance-to-ship, not hidden.

## 2. RAG: faithfulness vs recall@k are orthogonal audits

**What the literature says:**

1. **Faithful-and-wrong is the standard production failure.** Faithfulness audits the generator (claims ⊆ retrieved context); it never inspects whether the context is correct. Stale/wrong/adversarial retrieval → faithful repetition scores a perfect 1.0. Correct-and-ungrounded is the mirror failure (model answers from memory; retrieval untested). Gate on **groundedness ≥ threshold AND correctness ≥ threshold, never the average**; watch "grounded faithfulness" (both-true fraction) as the single line if forced. (dreaming.press 2026-07-02; LatentEval 2026-07-31; proofoftech 2026-05-16)
2. **Detector error profiles differ — pick your miss.** Groundedness classifiers (Vectara HHEM, Azure) run **high-precision/low-recall**; RAGAS-style claim-level faithfulness runs **high-recall/low-precision**; sentence-level checkers win short QA, long-context judges win summaries. RAGAS faithfulness is reference-free (no gold needed — the convenience and the blindness); context recall is the one metric that needs a reference. (same sources + RAGAS EACL 2024; Redis eval guide 2026-01-13)
3. **Read the 2×2, fix retrieval first.** Recall-low/faithfulness-high = retrieval fault (no prompt change recovers it); recall-high/faithfulness-low = generator fault; low-low → fix retriever first (faithfulness is a red herring). Blended single scores hide opposite regressions cancelling on the dashboard. Report recall + precision + faithfulness + answer-relevance separately with per-metric thresholds; fail CI builds on recall@5 drops >5pp. (dev.to gabrielanhaia 2026-06-13; amirulislamalmamun 2026-06-05)
4. **Intervals or noise.** Faithfulness 0.90 on n=20 → Wilson interval ≈0.70–0.97 (certifies nothing); on n=400 → ≈0.87–0.93. Every judge-made score inherits judge error + run variance on top of sampling error. (LatentEval 2026-06-22)

**What typical submissions do:** report recall@k (or precision on 500 queries) as "RAG works", or BLEU as "generation works", never both, no 2×2, no abstention test.

**What we do (`evaluation/RETRIEVAL_METRICS.md`, `evaluation/FAILURE_TESTS.md` F3, `evaluation/ABLATION.md`):**
- Retrieval proxy recall@1/3/5 = **1.000 (60/60)** explicitly labeled **availability/coverage, not relevance** — no judged relevant passages exist. Min top-1 score 0.222 = 2.8× the 0.08 gate, so the gate is a **safety net, not a discriminator**; recalibration (e.g. 0.25 near p10) queued as an honest gap.
- Answer-level groundedness (heuristic) reported **alongside, never instead**: final 4.75–4.83 mean, 100% ≥4, disclosed circular.
- Ablation isolates the contributions (human-60): no-retrieval esc_P 0.233 → final **0.400** (precision modulator), unresolvable 0.833→0.133, grounded 0.000→1.000; intent Δ 0.000 by design (classifier identical). Retrieval buys **precision + audit trail**, not intent accuracy — stated, not oversold.
- F3 abstention probe filed as **FAIL 1/2** (9-word link-only case auto-handles; fix queued: link-presence + low-information gate + per-intent score floor). Refusal-correctness queued per the "never refuse = lucky, not faithful" rule.

## 3. Escalation: precision/recall with asymmetric risk

**What the literature says (2025–2026 guides, all convergent):**

1. **Single confidence threshold is the most common production bug.** Deploy five triggers together: explicit human-request (instant, no negotiation), low-confidence + second-model QA gate, sentiment/sensitive-topic, VIP/high-value segment, action-needs-approval (refunds/cancellations/anything irreversible). Per-category thresholds (0.6 baseline, **0.8 on refunds/billing/cancellations**), repeat-fail cap (2 turns → escalate on 3rd). RLHF models are systematically miscalibrated (claimed 90% ≈ 75% actual) — set thresholds higher than feels natural on high-stakes intents. (eesel.ai 2026-06-09; bottis.ai 2026-06-23; tidereply 2026-06-06; open.cx 2026-05-13)
2. **Three timings, not one switch:** immediate (security/legal/money/human-request — any auto-reply is a liability), after-one-clarification (vague but recoverable, exactly one follow-up), after-failed-lookup (understood but ungroundable — clean handoff). Rule of thumb: higher cost-of-being-wrong → lower handoff bar; agent-minutes are cheap, wrong answers on money/safety are not. (tidereply)
3. **Warm handoff or CSAT death.** Minimum packet: 1-line issue summary + intent + verified account facts + what-AI-tried + sentiment + escalation reason + draft reply + owner/wait. 54% give up when context doesn't travel; 73% cite repeating themselves as top frustration. Never greet with "How can I help you" after a transfer. (eesel; bottis; thread-transfer 2025 playbook)
4. **Measure outcomes, not rate.** Escalation rate alone is vanity (traps inflate "automation"; nervous routing erodes it). Panel: escalation **precision** (necessary share) + **missed-escalation rate** (should-have-transferred) + time-to-ownership + repeat-contact 24–48h + post-escalation CSAT/FCR + context-completeness + agent-correction rate. Containment and resolution jointly; gap = problem size. (soon.works; eesel measuring guide 2025-10-27; open.cx)

**What typical submissions do:** no escalation policy, or single 0.7 threshold, no reason codes, no handoff packet, report accuracy only.

**What we do (`src/agent.py:decide_escalation`, `src/text_norm.py:features_for_escalation`, `evaluation/PER_INTENT.md`, `JUDGE_AGREEMENT_V2.md`):**
- 4 deterministic triggers with reason codes + signals dict on every output: can't-ground / policy-risk / frustration / human-request (incl. flame/burn lexicon fix, regression-tested).
- Full 2×2 published, both scales: human-60 `[[TN 34 FP 12][FN 6 TP 8]]` → P **0.400** / R **0.571** / F1 **0.471** (recall < 0.90 ship bar — stated; 12 FPs cheap, 6 FNs audited); human-200 acc **0.835** κ **0.487** P 0.469 R **0.767** F1 0.582.
- Safety slice: 11 human legal_safety cases, system escalate recall **0.909** (ship gate ≥0.90 — met on n=11, CI wide, stated).
- Handoff packet = intent + confidence + passage IDs + signals (warm-transfer minimum, transcript preserved upstream in TWCS threads).

## 4. Misleading metrics: containment, CSAT, BLEU — each contained

**What the literature says:**

1. **Containment = routing, not resolution.** "Contained" includes abandoned-in-frustration, stonewalled, and channel-switched sessions. Audit case: 61% containment with **38% FCR** — volume handled, fewer than 4 in 10 solved. Healthy bands (transactional 65–85%, conversational 50–65%) mean nothing without FCR ≥40–60% and CSAT 70–80% alongside; above-85% containment with poor resolution = containing frustration. Replacement stack: resolution quality + factual accuracy + escalation quality + repeat-contact + silent-abandon + policy adherence + cost-per-genuinely-resolved. Score 100% of conversations (2% sampling misses systematic AI failure clusters entirely). (kaizo 2026-07-27; parloa 2026-03-04; omniops 2026-02-24; netguru 2026-06-11; nugget 2026-05-06)
2. **Post-AI CSAT is self-selected + easy-queue-biased.** ~20% respond (range 5–60%); silent quitters — the worst failures — never answer; AI takes simple/high-volume contacts first so AI-vs-human CSAT comparisons are distribution artifacts. CSAT trails damage (lagging); leading signals: predicted-CSAT, completion <70% → CSAT <75% almost always, repeat-contact. (same set)
3. **BLEU/ROUGE ≈ noise for dialogue.** Liu et al. (EMNLP 2016, D16-1230, Twitter + Ubuntu corpora): BLEU-4 near-zero for a majority of pairs (only 4 examples >1e-9); weak correlation on Twitter, **zero** on technical Ubuntu; removing stopwords *weakens* BLEU-2 (sensitive to non-semantic factors); length-difference sensitivity ≫ human judgment. Task-oriented settings recover only moderate correlation, and only with multiple references (METEOR best of the lexical family). Single-reference BLEU-N can correlate *negatively* (Spearman) on DSTC2. (acl D16-1230; openreview task-oriented study)

**What typical submissions do:** headline containment/deflection, or CSAT from respondents, or BLEU script (`calculate_bleu.py`) as quality proof — the exact three the literature bans as launch evidence.

**What we do (`evaluation/BASELINE_VS_FINAL.md`, `research/evaluation/eval_strategy.md` §9, `docs/DIFFERENTIATION.md`):**
- BLEU deliberately **demoted to diagnostic-only** (r≈0.22–0.32 cited); headline = intent macroF1 + escalation P/R + heuristic groundedness + latency. No containment, deflection, CSAT, or AHT cited anywhere as evidence.
- §9 misleading-number disclosure printed as policy: word-overlap ≠ truth/safety; recall@k ≠ correctness; accuracy hides rare-intent collapse; judge scores valid only with reported agreement; static adversarial pass rates decay quarterly.
- Circularity published instead of trophied: weak-200 simple-keyword **1.000/1.000** labeled "do not cite — circular" (`results.csv` warning); headline is human-60 final **0.433/0.443** with κ 0.465 ceiling disclosed. A wrapper team ships the 1.000; we ship the 0.433 with the reason.

## 5. Failure analysis: taxonomy + open FAILs

**What the literature says:**

1. **Wrong-information hallucinations are the most severe.** Survey n=274: factual inconsistency outranks all other types; hidden/delayed-notice errors (acted-on wrong info) breach trust worse than immediately-visible ones; omissions rank least severe. User-perceived taxonomy from 3M app reviews: factual incorrectness **38%** (H1), nonsensical/irrelevant 25% (H3), fabricated 15% (H2) — top-3 = 78% of reports. Formal split: factuality (vs reality) vs faithfulness (vs input); intrinsic (contradicts context) vs extrinsic (unverifiable from source). Agent-level: reasoning/execution/perception/memorization/communication stages, each with own checks. (T&F 2025 Larsen; Nature SciRep 2025 app-review study; arxiv 2508.01781; arxiv 2509.18970)
2. **Canonical support failures are grounding + tool-gating failures.** Air Canada bereavement-discount hallucination (court-held liability), DPD profanity/jailbreak (guardrail bypass post-update, bot disabled <24h), Chevrolet $1 Tahoe (authority-override + no price-validation + no escalation path), Vanderbilt crisis-email (wrong-tool-for-empathy + review bypass). Fix pattern: input validation + authority limits + price/reasonableness checks + scope restrictions + human-approval on commitments + adversarial/red-team boundary testing pre-deploy. Single-layer defense always fails. (vectara awesome-agent-failures; genezio 2025-05-15)
3. **Production pattern = confident ungrounded answer + late/missing escalation;** opposite failure = over-eager escalation guidance collapsing resolution. Intercom Fin answers with 7-phase refine→validate→disambiguate-or-escalate + per-stage safety controls; community-observed failures: hallucinated features absent from cited sources, long off-topic replies unstopped without human interrupt. (Fin engine + community reports)

**What typical submissions do:** zero failure suite; or pass-only table; no adversarial prompts; no injection/PII/jailbreak probes.

**What we do (`evaluation/FAILURE_TESTS.md` F1–F8 + flame regression, `evaluation/ABLATION.md`, `evaluation/PER_INTENT.md`):**
- 17 probes, verdicts on current code: **13 PASS · 3 PARTIAL · 1 FAIL**, each with input→output→root-cause→queued-fix. FAIL (F3 link-only 9-word auto-handle), PARTIALs (F5 evil-URL auto-handle — safe draft, wrong decision; F6 PII×2 safe drafts, missing account_security escalate; F7 slang "batt" intent miss, safe escalate). None produces unsafe output today (no PII echoed — templates have no PII slots; no instruction complied with; no refund/action tool exists to hijack — the load-bearing architectural mitigation).
- Flame regression: pre-fix `other/auto` → post-fix `escalate/legal_safety` via lexicon add (fire/flame/burn/smoke/explod/shock/electrocut/bleed); residual intent miss disclosed (guardrail covers safety, PER_INTENT tracks hardware F1 0.00).
- Per-intent + confusion published (`PER_INTENT.md`, `confusion_human60.csv`, 11×11 INTENTS order): two collapsed classes (connectivity 0.00, hardware_device 0.00), top confusions enumerated (3× software_update→hardware, 3× connectivity→other, 3× purchase_billing→other…), week-2 prescriptions (2-turn context, carrier/SIM + safety lexicon, 200-human retrain, OOS calibration). n=60 CIs ±~12% stated; support ≤6 directional-only.

## 6. Head-to-head: typical submission vs ours

| Eval dimension | Typical submission (what the literature warns against) | Ours (artifact) |
|---|---|---|
| Golden set | None, or keyword-labeled test reused as proof (99.5%/1.000 "accuracy") | Dual golden: weak-200 (draft, circular, labeled) + human-60 (39/60 flips, headline) + human-200 (`golden_human_200.csv`; `GOLDEN_NOTE.md`) |
| Label agreement | Unreported | Weak-vs-human intent κ **0.465** / esc κ **0.015** disclosed; final-vs-human κs alongside; no inter-annotator κ yet — stated gap |
| Headline metric | Accuracy-only / BLEU / containment / CSAT | Intent acc + macroF1 **and** esc P/R/F1 **and** groundedness **and** latency; weak-200 shown only as circularity contrast (`BASELINE_VS_FINAL.md`) |
| Per-class honesty | Single number | Per-intent P/R/F1 + 11×11 confusion + top-7 confusions + collapsed-class callout (`PER_INTENT.md`, `confusion_human60.csv`) |
| Escalation | None / single threshold, no numbers | 4 triggers + reason codes; 2×2 both scales; safety recall **0.909** (n=11); recall <0.90 bar on human-60 disclosed |
| Retrieval vs generation | recall@k **or** BLEU, conflated | Proxy recall@k (coverage-labeled) **alongside** answer-level groundedness; ablation isolates each; 2×2 reading rule adopted |
| Judge | Unpinned LLM score / vibe | Heuristic ($0, deterministic) + pinned LLM hook (`gpt-4o-mini-2026-07-01`, temp 0, JSON-schema, double-run) behind wκ≥0.60 + safety-recall≥0.90 gate; zero LLM scores claimed |
| Misleading numbers | Cited as proof | Banned as proof (§9 disclosure in every report; BLEU diagnostic-only; no containment/CSAT) |
| Failure suite | None | F1–F8 (17 probes, 1 FAIL + 3 PARTIALs open) + flame regression (`FAILURE_TESTS.md`) |
| Ablation | None | 4-system ablation (rules = dominant for safety; retrieval = precision modulator; classifier = intent floor; templates = groundedness source) (`ABLATION.md`) |
| Cost / latency | Unreported ("scales") | Measured p50 **230ms**/p95 248ms e2e, retriever p50 46ms, 4.3 qps/1-worker, 42MB index; flat $6–50/mo ESTIMATE to 10k users vs linear LLM $0.0002–0.0005/req (`PERFORMANCE.md`, `COST.md`) |
| Baselines | Absolute-only | Trivial + keyword + no-retrieval + final deltas on both goldens; "final loses intent by design, wins escalation+groundedness" interpretation |

## 7. Moat bullets (return)

- **Dual golden with published flips + kappa ceilings** (weak-200 draft + human-200/60; 39/60 flips; weak-vs-human κ 0.465/esc 0.015) — competitors headline accuracy-only or keyword-circular 1.000s with no agreement numbers.
- **Chance-corrected, gated judging** (heuristic $0 judge + pinned `gpt-4o-mini-2026-07-01` hook behind wκ≥0.60 + safety-recall≥0.90; zero LLM scores faked) — literature (33–41pp kappa deflation; r=ρ=τ=φ=MCC identity; protocol swings 0.551→0.899) says uncorrected single-run judges are not proof; ours complies, theirs don't.
- **Retrieval and generation scored separately** (proxy recall@k coverage-labeled + answer-level groundedness + ablation showing retrieval = precision modulator esc_P 0.233→0.368) — faithful-but-wrong is the #1 production failure and recall-alone cannot see it.
- **Escalation as first-class output with asymmetric-risk accounting** (4 triggers + reason codes + handoff packet; 2×2 on human-60 and human-200; safety recall 0.909) — single-threshold systems are the documented production bug.
- **Misleading metrics contained by policy** (no containment/CSAT/BLEU-as-proof; §9 disclosure; BLEU diagnostic-only; circular 1.000 labeled do-not-cite) — the three numbers typical submissions headline are the three the literature bans.
- **Failure suite as spec with open FAILs** (F1–F8 13/3/1 + flame regression + per-intent collapsed classes + queued fixes) plus **ablation + measured cost/latency** — proof that loses honestly beats proof that wins circularly.

## 8. Queries + key sources (2026-09-10 websearch)

1. `LLM-as-judge agreement Cohen kappa vs correlation 2026` → arxiv 2606.00093 (binary-metric identity; protocol swings); arxiv 2606.19544 (21-judge, Δκ 33–41pp, MVVP); arxiv 2510.09738 (Judge's Verdict, κ̄ 0.801, Tier-1 0.781–0.816); latenteval.ai kappa-thresholds (no standard band; McHugh vs Landis&Koch).
2. `LLM judge position verbosity bias swap consistency 2025 2026` → arxiv 2604.23178 (style bias 0.76–0.92 dominates; swap model-dependent; CoT best on adversarial); spectrumofresearch 2026-06-24 (length-control 0.94→0.98 arena correlation); ijcnlp-2025 position-bias study (150k instances); arxiv 2603.01865 CyclicJudge; VERDICT-BENCH/JURY (single judge 87.6%→98.1%, probes 0.73→0.50).
3. `RAG faithfulness vs recall@k groundedness evaluation` → dreaming.press 2026-07-02; latenteval.ai 2026-07-31 + 2026-06-22 (CIs: n=20 ≈0.70–0.97 vs n=400 ≈0.87–0.93); proofoftech 2026-05-16; dev.to 2026-06-13 (2×2, fix-retrieval-first); amirulislamalmamun 2026-06-05.
4. `RAGAS faithfulness limitations hallucination metric 2025` → ai-tldr RAGAS explainer (targets: faithfulness >0.85, recall >0.80, precision >0.70); redis.io eval guide 2026-01-13 (faithfulness >0.9 high-stakes; CI-gated thresholds).
5. `customer support chatbot escalation precision recall human handoff threshold 2025` (+ `escalation precision recall asymmetric risk customer support triage`) → eesel.ai 2026-06-09 (5 triggers, 0.6/0.8 thresholds, warm-packet schema); bottis.ai 2026-06-23 (escalation precision vs continuity vs time-to-human); tidereply 2026-06-06 (3 timings, cost-of-wrong rule); open.cx 2026-05-13; soon.works (balanced scorecard); thread-transfer 2025 playbook (handoff CSAT >85%, repeat-question <5%).
6. `containment rate CSAT misleading metrics customer support chatbot 2025` → kaizo 2026-07-27 (containment rewards stonewalling; CSAT misses silent quitters; 7-metric replacement stack); parloa 2026-03-04; eesel.ai 2025-10-27 (True Resolution Rate; bad containment); omniops 2026-02-24 (75% containment/45% resolution gap; 20% CSAT response); nugget 2026-05-06 (AR% with backend verification); netguru 2026-06-11 (61%/38% audit).
7. `BLEU ROUGE correlation human judgment dialogue evaluation limits short replies` → Liu et al. EMNLP 2016 D16-1230 (BLEU-4 near-zero; weak Twitter / zero Ubuntu correlation); task-oriented follow-up (METEOR best; multi-reference required; single-ref BLEU-N negative Spearman on DSTC2).
8. `customer support chatbot failure modes hallucination error taxonomy 2025` → T&F 2025 (n=274 severity ranking); Nature SciRep 2025 (3M reviews; H1 38%/H3 25%/H2 15%); arxiv 2508.01781 (factuality vs faithfulness; intrinsic vs extrinsic); arxiv 2509.18970 (5-stage agent taxonomy); vectara awesome-agent-failures (Chevy/DPD/Vanderbilt); genezio 2025-05-15 (Air Canada liability case).

*Local artifacts audited:* `evaluation/{GOLDEN_NOTE,BASELINE_VS_FINAL,PER_INTENT,confusion_human60,JUDGE_AGREEMENT,JUDGE_AGREEMENT_V2,ABLATION,RETRIEVAL_METRICS,PERFORMANCE,COST,FAILURE_TESTS,rubric,judge}.md/py/csv` · `research/{competitors/analysis,evaluation/eval_strategy,papers/academic_review}.md` · `docs/DIFFERENTIATION.md` (V1).
*Honest gaps carried forward:* single annotator (no inter-annotator κ); heuristic judge not yet κ-scored; retrieval proxy unjudged; n=60 CIs ±~12%; safety recall n=11; latency single-worker, no p99/concurrency/RSS.
