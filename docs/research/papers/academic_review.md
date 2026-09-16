# Academic Review: Short-Text Intent Classification, RAG Grounding, LLM-as-Judge Agreement
**Agent 8 — Academic Research for Hiver**
**Date:** 2026-09-10 (UTC)
**Scope:** Banking77 / Twitter short-text intent classification with limited labels; retrieval-augmented response generation for support; hallucination/groundedness metrics; LLM-as-judge bias and human agreement (Cohen's kappa).
**Output contract:** 8–10 web searches → 5–8 key papers with useful-vs-not-feasible + verified-vs-hypothesis → implications for our eval (why a 50–100-pair judge–human agreement study).

> Honesty convention used below: **[VERIFIED]** = confirmed by a search excerpt / abstract / leaderboard snippet in this session. **[HYPOTHESIS / NEEDS PDF]** = plausible inference or single-source claim not yet confirmed by reading the full PDF. Do not treat hypotheses as facts.

## Search log (10 queries, 2026-09-10)

1. `Banking77 intent classification SOTA 2024 2025 accuracy` (deep, 8 results)
2. `arXiv few-shot intent classification limited labels 2024 2025 SetFit` (deep, 8)
3. `Twitter short text classification emotion sentiment SOTA 2024 2025 arXiv` (deep, 8)
4. `retrieval-augmented response generation customer support 2024 2025 arXiv` (deep, 8)
5. `hallucination groundedness faithfulness metrics RAG factuality 2024 2025` (deep, 8)
6. `LLM-as-judge bias human agreement Cohen kappa 2024 2025` (deep, 8)
7. `RAGAS faithfulness answer relevancy RAG evaluation metrics 2024` (deep, 8)
8. `Papers With Code Banking77 leaderboard SOTA 2025 DeBERTa accuracy` (deep, 8)
9. `MT-Bench AlpacaEval LLM judge position verbosity self-enhancement bias human agreement` (deep, 8)
10. `Lewis et al retrieval-augmented generation RAG original paper grounded generation citations` (fast, 8)

---

## 1. Banking77 — the benchmark to beat (foundational, not SOTA-novel)

**Paper:** Casanueva et al., PolyAI, *"Efficient Intent Detection with Dual Sentence Encoders"* (2020) — dataset paper for Banking77. **[VERIFIED — dataset facts corroborated across 4+ excerpts]**
- URLs:
  - Dataset card / mirror: https://github.com/aahrong/banking77
  - TFDS mirror with full label list + splits: https://www.tensorflow.org/datasets/community_catalog/huggingface/banking77?hl=zh-cn
  - SOTA aggregator (use with caution): https://www.wizwand.com/dataset/banking77
- What it is: 13,083 online-banking queries, 77 fine-grained single-domain intents, train 10,003 / test 3,080, avg ~11–12 words (~55–60 chars). Designed to be harder than small (<10-class) corpora (SNIPS, AskUbuntu) and complementary to multi-domain CLINC150/HWU64. **[VERIFIED]**
- Baselines reported in later papers citing it: BERT fine-tune full-data ≈ 93.6–93.66% accuracy; 10-shot ≈ 85.1–85.19% (USE + ConveRT dual encoder); 30-shot ≈ 90.57%. **[VERIFIED via Loukas-related excerpts citing Casanueva]**
- Community full-data points: DistilBERT fine-tunes report 90.8–92.44% accuracy / ~0.924 macro-F1 (HF model card + GitHub repo). **[VERIFIED as community claims, not peer-reviewed]**
- Label-noise finding: Ying & Thomas (cited in Loukas) used confident learning + cosine similarity to build a "trimmed" set → 92.4% acc / 92.0 F1 (+4.5pp). **[VERIFIED as cited claim; NEEDS PDF to confirm exact split]**
- **Useful for Hiver:** adopt Banking77 splits + macro-F1 (not just accuracy) as the primary intent metric; budget an error-analysis pass for overlapping pairs (e.g. `pending_transfer` vs `pending_card_payment`, `exchange_rate` vs `exchange_charge`) — community error analysis says ambiguity, not capacity, dominates errors. **[VERIFIED — community error-analysis excerpt]**
- **Not feasible / not transferable:** full-data 93%+ numbers assume clean, single-turn, English banking queries. Our support data (multi-turn, noisy, possibly Twitter-style) will score lower; do not promise 93% on Hiver data. OOS (out-of-scope) handling is a separate task (see DETER below) — Banking77 alone does not evaluate rejection. **[HYPOTHESIS grounded in DETER + Banking77 design]**

## 2. Resource-limited Banking77 with LLMs + RAG few-shot (most directly applicable)

**Papers:** Loukas et al., *"Making LLMs Worth Every Penny: Resource-Limited Text Classification in Banking"* (arXiv:2311.06102, 2023; ACM version 2024) + follow-up *"Lending an Ear: How LLMs Hear Your Banking Intentions"* (2024, Llama-3/Mistral/Gemma-2/Falcon + expert-selected shots + RAG). **[VERIFIED — excerpts from arXiv PDF + both ACM HTML pages]**
- URLs:
  - https://arxiv.org/pdf/2311.06102
  - https://dl.acm.org/doi/fullHtml/10.1145/3604237.3626891
  - https://dl.acm.org/doi/fullHtml/10.1145/3677052.3698608
- Key results **[VERIFIED as reported claims]**:
  - Standard few-shot with 77 labels is prompt-heavy (e.g. 3-shot = 231 examples per inference call).
  - RAG few-shot (retrieve only top-k similar examples per query, ~2.2% of the classic prompt in the follow-up) preserves/cuts cost dramatically: Claude 2 + RAG ≈ 22× cheaper than GPT-4 path (~$700 saved in their study) at higher accuracy.
  - 1-shot: Claude 2 ≈ GPT-3.5 at ~half the cost. 10-shot and full-data LLM/MLM numbers track §1.
  - Expert-curated 3-per-intent examples beat random sampling in few-shot (SME-selected top-3 from 10 random). **[VERIFIED]**
- **Useful for Hiver:** copy this exact pattern — (a) retriever (MPNet / `all-mpnet-base-v2`, cited as their sentence-encoder choice) → top-k exemplars → small LLM classifier; (b) 10-shot and RAG top-k as the two few-shot conditions to report; (c) cost-per-1k-inferences column next to accuracy (their core contribution is cost×accuracy, not accuracy alone).
- **Not feasible:** absolute dollar figures ($700, 22×) are provider-price- and date-sensitive (2023 Claude/GPT-4 pricing) — recompute on current inference costs; do not quote as current. Their "higher score at lower cost" holds directionally but the multiplier will differ. **[HYPOTHESIS — needs repricing]**
- Uncertainty: I did not verify their test subsample size or whether trimmed vs raw Banking77 was used in each table — read Tables 1–2 of the PDF before copying numbers into our eval plan. **[NEEDS PDF]**

## 3. Few-shot with limited labels: SetFit + "just fine-tune" (method choice)

**Papers:** Tunstall et al., *"Efficient Few-Shot Learning Without Prompts (SetFit)"* (arXiv:2209.11055, 2022) + Zhang et al., *"Revisit Few-shot Intent Classification: Direct Fine-tuning vs. Continual Pre-training"* (arXiv:2306.05278, ACL Findings 2023). **[VERIFIED — abstracts + HF blog + GitHub]**
- URLs:
  - https://arxiv.org/abs/2209.11055
  - https://huggingface.co/blog/setfit
  - https://github.com/huggingface/setfit
  - https://arxiv.org/abs/2306.05278
  - Related multi-label extension: https://arxiv.org/html/2410.05770v1 (FusionSent vs SetFit, 2/4/8 shots)
- Claims **[VERIFIED]**:
  - SetFit: contrastive fine-tune of a sentence transformer on pairs/triplets from few labels → train small classifier head; no prompts/verbalizers; e.g. 8 shots/class on Customer Reviews ≈ RoBERTa-Large on full 3k; RAFT-competitive at ~355M params vs GPT-3 scale; ~order-of-magnitude faster than PET/PEFT.
  - Zhang: direct fine-tuning of PLMs on ≥2 shots/class already beats many continual-pretraining pipelines; gap shrinks as labels grow; context augmentation + sequential self-distillation help most at 1–2 shots.
  - Active/human-in-loop note (arXiv:2401.09555): "label a few, model labels the rest" with entropy/probability triage beats zero-shot LLMs on Banking/Finance Phrasebank-style tasks — small study, limited models. **[VERIFIED as preprint claim]**
- **Useful for Hiver:** SetFit (or `all-mpnet-base-v2` + logistic head) is the right *cheap baseline* for Banking77 5/10-shot and for cold-start intents where we have <10 examples; direct fine-tune of a small encoder (DistilBERT/DeBERTa-v3-small) is the second baseline before any LLM judge/generator. Report mean±std over 3 seeds — few-shot variance is high (±10pp cited in IntentBERT tables). **[VERIFIED — variance warning in excerpts]**
- **Not feasible:** SetFit does not solve 77-way 1-shot with overlapping labels — expect 1-shot ≈ weak; do not present SetFit as beating GPT-4+RAG at 1-shot on Banking77 (Loukas shows retrieval+LLM wins there). Multilingual SetFit = just swap the ST body, but dialect/arabized results (ArBanking77: MSA F1 0.921 vs Palestinian-dialect 0.900, gap closes ~5pp with augmentation) warn that short/dialectal text needs augmentation. **[VERIFIED — ArBanking77 excerpt https://arxiv.org/pdf/2310.19034]**

## 4. Twitter / short-text emotion (proxy for short support utterances)

**Papers:** SmallEnglishEmotions study (arXiv:2402.16034, 2024) + Albu & Spînu BERT+SVM ensemble (2022) + SemEval-2025 Task 11 systems (BRIGHTER). **[VERIFIED — abstracts/excerpts; SOTA is fragmented, treat numbers as dataset-specific]**
- URLs:
  - https://arxiv.org/pdf/2402.16034
  - https://arxiv.org/abs/2208.04547
  - https://arxiv.org/abs/2503.20163
  - https://aclanthology.org/2025.semeval-1.243.pdf
- Claims:
  - SmallEnglishEmotions: 6,372 tweets, 20–70 words (avg ~50), 5 classes (happiness/sadness/anger/fear/other, Jack model); transfer learning + DistilBERT/BERT embeddings best among tested classical+DL methods. **[VERIFIED]**
  - Albu: 4 emotions + neutral, BERT+SVM ensemble ≈ 0.91 accuracy on their extended balanced set. **[VERIFIED as reported, single split]**
  - Golchin & Riahi 2025: BiLSTM+CNN ≈ 0.93 avg accuracy on 4-class Twitter set. **[VERIFIED as reported; small-study caveat]**
  - SemEval-2025 trend: ensembles of `cardiffnlp/twitter-roberta-large-emotion-latest` + `SamLowe/roberta-base-go_emotions` + full fine-tune + classification head; LLM SFT + CoT + augmentation for low-resource tracks. **[VERIFIED]**
- **Useful for Hiver:** for Twitter-length inputs: prefer domain-pretrained encoders (`twitter-roberta`) over generic BERT; single-emotion-per-text annotation simplifies labeling (mirrors our single-intent-per-utterance setup); hashtag/emoji handling + lexicon+Vader/GloVe features still help classical baselines per SemEval-2018-era ablation (Hutto/Vader + DepecheMood + GloVe-Twitter). **[VERIFIED — SemEval E-c ablation excerpt]**
- **Not feasible / caution:** 0.91–0.93 Twitter numbers are on small/balanced/curated sets, not wild Twitter; multi-label + intensity tracks (SemEval-2025) are harder and need different metrics (micro/macro-F1, Pearson). Do not compare our macro-F1 on 77-way Banking77 with 4–5-way Twitter accuracy. **[HYPOTHESIS — methodological caution, standard practice]**

## 5. RAG foundations + KG-RAG for customer support (generation side)

**Papers:** Lewis et al., *"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"* (NeurIPS 2020) + Xu et al., *"Retrieval-Augmented Generation with Knowledge Graphs for Customer Service QA"* (SIGIR 2024, LinkedIn deployment). **[VERIFIED]**
- URLs:
  - http://arxiv.org/abs/2005.11401
  - https://arxiv.org/abs/2404.17723
  - https://arxiv.org/html/2404.17723v2
  - Supporting 2025 e-commerce KG-RAG (single-author, weaker evidence): https://arxiv.org/abs/2509.14267
  - Agent-in-the-loop flywheel (production pilot, 5k cases, +11.7% R@75 / +8.4% helpfulness / +38% citation acc): https://arxiv.org/html/2510.06674v1
- Claims **[VERIFIED]**:
  - Lewis: DPR retriever + BART generator jointly fine-tuned; SOTA on 3 open-domain QA; more specific/diverse/factual than parametric-only seq2seq; can answer 11.8% even when answer not in retrieved docs (NQ).
  - Xu (strongest support-domain evidence): KG built from historical tickets preserves intra-issue structure + inter-issue relations; +77.6% MRR and +0.32 BLEU over plain-text RAG; ~6 months in LinkedIn CS → −28.6% median per-issue resolution time.
  - Hong et al., EMNLP-Industry 2025 (compliance angle): retrieval-based Match-and-Respond with LLM-generated *similar questions* for KB expansion → hallucination-free, compliance-guaranteed path for regulated CS. Useful counterpoint to pure generation: https://aclanthology.org/2025.emnlp-industry.51.pdf **[VERIFIED]**
- **Useful for Hiver:** two-track response strategy — (A) retrieval-based verified-answer path for compliance-sensitive intents, (B) KG/RAG generative path for long-tail; log MRR/Recall@K + BLEU/ROUGE/METEOR as in Xu, plus resolution-time proxy if agents-in-loop.
- **Not feasible:** KG construction over tickets + entity linking is a project, not a sprint — start with hybrid BM25+dense (as in Patel §3: BM25 + sentence-transformers) and add KG subgraphs only if retrieval precision stalls. Patel's "+23% factual accuracy / 89% satisfaction" is a single-author 2025 preprint on 10k private queries — cite as **[HYPOTHESIS, NEEDS REPLICATION]**, not as a target.

## 6. Grounding/factuality metrics: RAGAS, ARES, FaithJudge, GaRAGe (eval side)

**Papers:** Es et al., *"RAGAS: Automated Evaluation of Retrieval Augmented Generation"* (arXiv:2309.15217, 2023) + Saad-Falcon et al., *"ARES"* (2023) + Vectara *"Benchmarking LLM Faithfulness in RAG with Evolving Leaderboards / FaithJudge"* (arXiv:2505.04847, 2025) + GaRAGe (arXiv:2506.07671, 2025). **[VERIFIED — excerpts incl. formulas and head-to-head tables]**
- URLs:
  - https://arxiv.org/html/2309.15217v1
  - https://docs.ragas.io/en/v0.1.21/concepts/metrics/faithfulness.html
  - https://arxiv.org/html/2311.09476v2 (ARES)
  - https://arxiv.org/html/2505.04847v1 (FaithJudge)
  - https://arxiv.org/html/2506.07671v1 (GaRAGe RAF score)
  - https://arxiv.org/html/2407.12873v1 (telecom RAGAS validation)
  - https://arxiv.org/pdf/2605.14488 (Deepchecks vs RAGAS vs LangSmith head-to-head)
- Definitions **[VERIFIED]**:
  - RAGAS Faithfulness = |claims inferable from context| / |all claims| (claim-decompose → verdict per claim). Answer Relevance = mean cosine(q, generated-q_i). Context Relevance = relevant-sentences / all-context-sentences. Answer Correctness = weighted Factual-Correctness (TP/FP/FN F1) + Answer Similarity.
  - RAGAS WikEval human agreement: Faith 0.95 / AnsRel 0.78 / CtxRel 0.70 (pairwise, 2 annotators, ~95%/90% inter-annotator). Beats vanilla GPT-score/rank prompts. **[VERIFIED]**
  - Cracks **[VERIFIED]**: ARES beats RAGAS by ~59pp (context rel.) and ~14pp (answer rel.) on KILT/SuperGLUE ranking; telecom study finds Factual Correctness + Faithfulness jointly predict expert correctness, Answer Relevance unstable, and Faithfulness↔Factual-Correctness negatively correlate under wrong retrieval (correct answer from wrong context = unfaithful but "correct" — RAG should have abstained); Deepchecks Grounded-in-Context ROC-AUC 0.84–0.92 vs RAGAS-Faithfulness(GPT-4o) 0.65–0.83; FaithBench notes low human agreement on benign/questionable hallucinations; EMNLP-2025 "Mirage" study: metrics often misalign with humans and don't scale cleanly with size.
  - Advances to copy: FaithJudge (judge sees few human-annotated peer responses to same source before ruling — beats zero-shot judges); GaRAGe RAF = % answers eligible AND supported by *relevant* passages + deflection expectation when grounding insufficient + per-passage attribution.
- **Useful for Hiver:** adopt Faithfulness + Factual/Answer Correctness as the gating pair; use Context Relevance/Precision for retrieval tuning only (not gating); require abstention/deflection metric when retrieval is weak; prefer claim-level verdicts over whole-answer scores.
- **Not feasible:** running RAGAS out-of-the-box with default prompts as a quality gate — ARES/telecom/Deepchecks evidence says it overstates context/answer relevance and understates faithfulness failures. Any threshold (e.g. faithfulness ≥ 0.8) must be calibrated on our own 50–100 human-labeled pairs (§8). Also note RAGAS needs ground-truth answers for correctness metrics — budget their creation. **[HYPOTHESIS → validated by proposed study]**

## 7. LLM-as-judge: biases + agreement ceilings (why calibration is mandatory)

**Paper:** Zheng et al., *"Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"* (NeurIPS 2023). **[VERIFIED — full HTML excerpt with tables]**
- URL: http://arxiv.org/html/2306.05685v4
- Claims **[VERIFIED]**:
  - GPT-4 judge ≈ 80%+ agreement with humans ≈ human–human level; agreement rises 70%→~100% as model-pair quality gap widens.
  - Biases: position bias (only GPT-4 consistent >60% on swaps; Claude-v1 23.8% default, strongly first-biased), verbosity bias ("repetitive list" attack fails 91.3% for Claude/GPT-3.5 vs 8.7% GPT-4), self-enhancement inconclusive ("cannot determine" with limited data), math/reasoning grading weak (default fail 14/20 → CoT 6/20 → reference-guided 3/20).
  - Mitigations that work: swap-and-require-both-orders-win (conservative), reference-guided + CoT judge, show full conversation not split turns.
- **Useful for Hiver:** copy all three mitigations into our judge prompt + pipeline (swap, reference answer, CoT-then-verdict JSON); never report pairwise win-rates without swap-consistency %.
- **Not feasible:** assuming 2023 GPT-4 numbers transfer to our judge model/task — verbosity/position bias is model- and prompt-specific; must remeasure. Also MT-Bench is open-ended chat, not support QA with grounding — our judge needs grounding-aware rubrics (see §6/§8).

## 8. Quantifying judge quality with kappa + bias audits (protocol template)

**Papers:** Han et al., *"Judge's Verdict"* (arXiv:2510.09738, 2025; 54 LLMs as RAG/agentic judges) + Chen et al., *"Humans or LLMs as the Judge? A Study on Judgement Bias"* (EMNLP 2024) + 2026 large-scale audit (21 judges, ~541k judgments, arXiv:2606.19544 — from excerpt, treat as preprint). **[VERIFIED — excerpts with formulas and counts]**
- URLs:
  - https://arxiv.org/abs/2510.09738
  - https://aclanthology.org/2024.emnlp-main.474
  - https://arxiv.org/pdf/2606.19544 (large audit; verify before citing as published)
- Claims **[VERIFIED]**:
  - Han: two-step — (1) correlation filter, (2) Cohen's κ = (Po−Pe)/(1−Pe) + "Turing test" z = (κ_LLM − μ_human)/σ_human; human–human κ̄ = 0.801 (1,994 items × 3 annotators); 27/54 Tier-1 (23 human-like |z|<1, 4 super-consistent z>1); size ≠ judge quality; key demo: r=0.95 but κ=0.45 when judge is systematically harsh — correlation alone lies.
  - Chen: both humans and LLMs show misinformation-oversight, gender, authority, beauty biases; biases are exploitable as attacks — no judge (human or LLM) is bias-free.
  - 2026 audit (preprint): κ-deflation (EM − κ) 33–41pp universal on MT-Bench; rankings shift up to 14 places across benchmarks; test–retest >0.95 coexists with severe position bias; verbosity = corr(length-diff, verdict).
- **Useful for Hiver:** this is the exact template for our 50–100-pair study (§9): report κ (primary), Krippendorff's α, tie-excluded EM, swap-consistency, verbosity correlation, and z-vs-human; pre-register Tier-1 = κ within human band AND |z|<1 AND swap-consistency ≥85%.
- **Not feasible:** Han's κ̄=0.801 will not replicate on harder support items (FaithBench low agreement on ambiguous cases) — set the bar as "match *our* human–human κ on *our* sample," not 0.8. Multi-agent debate/meta-judge reduces some bias but can amplify bandwagon/CoT bias per EMNLP-2025 multi-agent study — do not add debate judges before the base judge is calibrated. **[HYPOTHESIS, consistent with excerpts]**

---

## Cross-cutting SOTA snapshot (do not quote without checking splits)

| Task | Best verified number in session | Source |
|---|---|---|
| Banking77 full-data accuracy | ~93.6–93.8% (BERT / best cited) | Casanueva via Loukas; Ying trimmed 92.4% |
| Banking77 10-shot | ~85.2% (USE+ConveRT); aggregator claims up to 87.95% 10-shot | Loukas citing Casanueva; Wizwand **[UNVERIFIED aggregator]** |
| Banking77 5-shot | ~78.9–79.1% | Wizwand **[UNVERIFIED]** |
| Twitter 4–5-way emotion accuracy | 0.91–0.93 (curated, balanced) | Albu; Golchin **[small-study]** |
| RAG support retrieval | +77.6% MRR (KG-RAG vs plain RAG) | Xu SIGIR'24 |
| RAG judge–human agreement | ~80% / κ̄≈0.80 (MT-Bench, GPT-4) | Zheng; Han |
| RAGAS faithfulness human agreement | 0.95 pairwise (WikEval) | Es et al. |
| Automated faithfulness SOTA direction | FaithJudge (few-shot w/ peer annotations) > zero-shot judges | Vectara 2025 |

Banking77 Papers-With-Code-style leaderboard could not be verified live this session (Papers With Code entries returned DeBERTa-paper and CodeSOTA pages, not a Banking77 board) — use Wizwand only as a pointer and verify each number against its paper. **[HONEST GAP]**

## Implications for our eval — why a 50–100-pair judge–human agreement study is required

1. **Correlation lies; kappa tells the truth.** Han's harsh-judge demo (r=0.95, κ=0.45) plus the 33–41pp EM−κ deflation means our judge could look "80% accurate" while being systematically lenient/harsh or position-biased. Only chance-corrected κ (+ α) on our own items exposes this.
2. **RAGAS defaults don't transfer.** ARES/telecom/Deepchecks evidence (§6) shows faithfulness and answer-relevance prompts misrank systems out-of-the-box and that "correct-but-unfaithful" (wrong retrieval) cases invert the metrics. Thresholds (e.g. ship iff faithfulness ≥ X) are meaningless until calibrated against human verdicts on *our* contexts.
3. **Our domain is the hard corner.** 77 overlapping intents + short/noisy queries + ambiguous hallucinations (benign/questionable) is exactly where FaithBench reports low human agreement. If humans disagree, the judge can't be "right" — we need our own human–human κ to set the ceiling the judge must match (not 0.801 from Han's data).
4. **Biases are exploitable, not theoretical.** Position/verbosity/authority/beauty attacks (Zheng, Chen) mean an uncalibrated judge can be gamed by longer or first-placed answers. The study must include swap-consistency and a verbosity attack subset to prove the pipeline (swap + reference-guided + CoT) actually mitigates them here.
5. **Why 50–100 pairs (not 10, not 1,000):** 10 pairs cannot estimate κ (CI spans ~0.5); 1,000 pairs costs annotator-weeks before the rubric is stable. 50–100 stratified pairs (by intent cluster × retrieval quality × answer correctness, incl. ~20% wrong-retrieval and ~15% ambiguous/deflect cases) gives a κ CI width ≈ ±0.15–0.20 at moderate agreement — enough to distinguish κ<0.6 (reject/iterate) from κ≥0.7 (accept with monitoring), calibrate RAGAS/FaithJudge thresholds, and run swap-replicates (×2) without doubling annotation cost. This matches precedent: RAGAS WikEval, ARES PPI, and telecom validations all draw conclusions from hundreds (not thousands) of labels; Han scales up only *after* the protocol is fixed.
6. **Proposed protocol (for eval owner to approve):** sample 75 pairs (50 grading + 25 attack/swap reserve); 2 blinded humans + judge; rubric = faithfulness (claim-level) + answer correctness + abstention-correctness; report κ_LLM–human (mean over humans), human–human κ, α, EM, swap-consistency, verbosity-corr, z-score; pre-register Tier-1 (κ within human band, |z|<1, swap ≥85%); on fail, iterate prompt (reference+CoT) once then re-sample 25 fresh pairs — never tune to the test pairs.

## Open uncertainties (explicit)

- Exact Banking77 5/10-shot SOTA today (aggregator numbers unverified; need paper-by-paper check).
- Whether Loukas tables use raw vs trimmed Banking77 per condition (needs PDF Tables).
- Current $/1k-inference for our shortlisted judge+embedder (2023 cost claims stale).
- Our human–human κ on support QA (could be well below 0.8; the study exists to measure it).
- Live Papers-With-Code Banking77 board URL (not resolved this session).

## References (URLs visited / cited)

- Banking77 data: https://github.com/aahrong/banking77 · https://www.tensorflow.org/datasets/community_catalog/huggingface/banking77?hl=zh-cn · https://www.wizwand.com/dataset/banking77
- Loukas 2023: https://arxiv.org/pdf/2311.06102 · https://dl.acm.org/doi/fullHtml/10.1145/3604237.3626891
- Lending-an-Ear follow-up: https://dl.acm.org/doi/fullHtml/10.1145/3677052.3698608
- SetFit: https://arxiv.org/abs/2209.11055 · https://huggingface.co/blog/setfit · https://github.com/huggingface/setfit
- Revisit few-shot: https://arxiv.org/abs/2306.05278 · IntentBERT: https://arxiv.org/html/2109.05782v2 · FusionSent: https://arxiv.org/html/2410.05770v1 · Active loop: https://arxiv.org/html/2401.09555v1 · Coarse-to-fine multi-label: https://aclanthology.org/2024.findings-emnlp.140
- ArBanking77: https://arxiv.org/pdf/2310.19034 · DETER OOS: https://aclanthology.org/2024.lrec-main.763.pdf
- Twitter: https://arxiv.org/pdf/2402.16034 · https://arxiv.org/abs/2208.04547 · https://arxiv.org/abs/2503.20163 · https://aclanthology.org/2025.semeval-1.243.pdf
- RAG orig: http://arxiv.org/abs/2005.11401
- KG-RAG support: https://arxiv.org/abs/2404.17723 · https://arxiv.org/html/2404.17723v2 · https://arxiv.org/abs/2509.14267 · https://arxiv.org/html/2510.06674v1 · Compliance SQG: https://aclanthology.org/2025.emnlp-industry.51.pdf
- RAGAS: https://arxiv.org/html/2309.15217v1 · https://docs.ragas.io/en/v0.1.21/concepts/metrics/faithfulness.html · ARES: https://arxiv.org/html/2311.09476v2 · Telecom: https://arxiv.org/html/2407.12873v1 · Deepchecks: https://arxiv.org/pdf/2605.14488 · FaithJudge: https://arxiv.org/html/2505.04847v1 · GaRAGe: https://arxiv.org/html/2506.07671v1 · Mirage: https://aclanthology.org/2025.findings-emnlp.1035
- Judge: http://arxiv.org/html/2306.05685v4 · https://arxiv.org/abs/2510.09738 · https://aclanthology.org/2024.emnlp-main.474 · https://arxiv.org/pdf/2506.19544 · https://arxiv.org/pdf/2506.22316v1
