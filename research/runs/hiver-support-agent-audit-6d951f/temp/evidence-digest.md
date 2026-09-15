# Evidence digest — hiver-support-agent-audit-6d951f

Method: no claims-*.json existed (fetchers write notes directly), so this digest is orchestrator-assembled
from interim-note committed positions, consensus-claims.json, contradiction-graph.json, source-tensions.json,
and gap-fill fetcher reports. Verbatim passages are quoted from note bodies read in full during steps 5-8.
Counts as the step-10 primary-evidence index.

### Atomic item: intent classifier architecture (SetFit-first + uncertainty routing)

- Hybrid SetFit + MC-dropout routing lands within ~2% of native-LLM F1 at ~50% reduced latency (empirical, Arora hybrid)
  > "with the hybrid system we are able to bring performance gap further down to ~2% (from ~6%) for all datasets for which train and test data were from same distribution"
  [intent-detection-in-the-age-of-llms]
- SetFit ~56x faster than best LLM; negative augmentation +>5% (empirical)
  > "SetFit is about 56 times faster than overall best LLM (v3 Haiku)"
  [intent-detection-in-the-age-of-llms]
- RAG-filtered dynamic few-shot: Claude 2 K=20 → 85.5% at $42 BEATS GPT-4 full-prompt 83.1% at $740 (empirical, Loukas)
  > "Dynamic/RAG few-shot (retrieve top-K=5/10/20 by MPNet cosine, 1 call per query): Claude 2 K=20 → 85.5% at $42 BEATS GPT-4 classic 3×77=231 demos 83.1% at $740"
  [interim-setfit-vs-llm-intent-with-uncertainty-routing]
- GPT augmentation helps only for distinct intents; bleeds into neighbor intents when close (empirical, Sahu 2022)
  > "GPT-generated data significantly boosts the performance of intent classifiers when intents in consideration are sufficiently distinct from each other"
  [data-augmentation-for-intent-classification-with-off-the-shelf-large-language-mo]
- Nothing consistently beats MaxProb across 17 datasets × IID/OOD/ADV (empirical, Varshney Findings-2022)
  > "none of the existing approaches consistently and considerably outperforms MaxProb in all three settings"
  [investigating-selective-prediction-approaches-across-several-tasks-in-iid-ood-an]
- Full-layer MC-dropout CAN beat MaxProb on in-domain text-class rejection (empirical, Shelmanov ACL-2022)
  > "standard MC-dropout (ALL dropout layers on) gives big improvements over SR/MaxProb on SST-2/CoLA/MRPC + accuracy-rejection curves (MRPC 88.4→96.0% at 80% coverage, +1.3pp over SR)"
  [gap-fill cc-2 report: uncertainty-estimation-of-transformer-predictions-for-misclassification-detectio]
- LLM OOS-AUCROC degrades faster than encoders as scope/label-count grow (empirical controlled experiment)
  > "fine grained labels and smaller label spaces are better for LLM's OOS detection capabilities"
  [intent-detection-in-the-age-of-llms]
- ZSL-LLM trails discriminative SOTA badly except tiny-N; OOD inverted-U with more demos (empirical, Wang 2024)
  > "ZSD-LLM trails discriminative SOTA badly (Banking-50%: IND-ACC −13.4, OOD-Recall −56%, OOD-F1 −47% vs UniNL)"
  [interim-setfit-vs-llm-intent-with-uncertainty-routing]
- Noisy-tweet benchmark favors Twitter-pretrained backbones over SetFit-once-run (empirical, Loerakker CASE-2024)
  > "Twitter-pretrained Bernice/TwHIN-BERT beat mBERT/BERTje/LR; SetFit run once, did NOT beat them and trained substantially slower"
  [gap-fill cc-2 report: fine-tuning-language-models-on-dutch-protest-event-tweets-acl-anthology]
- Banking77: 10,003 train / 3,080 test, clean single-domain banking English — explicitly NOT Twitter (dataset fact)
  [polyaibanking77-datasets-at-hugging-face]

### Atomic item: retrieval (hybrid + rerank over thread windows)

- Pure dense fails silently on exact identifiers; returns something, LLM writes fluent confident wrong-specifics reply, no error fires (mechanism, 5-source convergent)
  > "Pure dense retrieval fails silently on exact identifiers, code, and rare terms"
  [hybrid-search-in-production-why-bm25-still-wins-on-the-queries-that-matter]
- Turion stack: dense-only R@10 0.67 → hybrid RRF 0.78 (+11pts) → +rerank 0.84 (+30% over dense) (empirical)
  [interim-hybrid-retrieval-payoff]
- WANDS: naive RRF +~1.2% blended; tuned hybrid + field-boosting +7.4-7.5% (empirical)
  [interim-hybrid-retrieval-payoff]
- Anthropic contextual stack: −35% failures (embeddings) → −49% (+BM25) → −67% (+rerank) (empirical, cross-domain)
  [contextual-retrieval-in-ai-systems-anthropic]
- Hybrid lift +8-15% concentrated almost entirely on exact-term queries (empirical, gap-fill)
  [gap-fill cc-3 report: why-dense-retrieval-fails-on-acronyms-ids-and-code-and-how-hybrid-fixes-it-pradh]
- SPLADE learned-sparse matches hybrid quality but query-expansion latency up to ~6× BM25 unless doc-only (engineering)
  [gap-fill cc-3 report: splade-vs-bm25-vs-dense-does-learned-sparse-retrieval-beat-hybrid-search]
- pgvector + tsvector + RRF-in-one-SQL concrete recipe exists (engineering)
  [gap-fill cc-3 report: how-to-build-hybrid-search-with-pgvector-and-bm25-in-postgres-ben-moataz]
- RRF k=60 cold start; migrate to cross-validated weighted-α (expect ≈0.3 sparse-heavy for identifier loads) once ≥40 relevance pairs (practice rule, convergent)
  [interim-hybrid-retrieval-payoff]
- Rerank ≤50 candidates (30-50 → 100-200ms); needing 200+ signals broken first-stage recall (practice rule)
  [interim-hybrid-retrieval-payoff]
- First-stage latency non-issue at this scale (all stores <30ms <1M vectors); reranker dominates e2e (benchmark table)
  [chromadb-vs-qdrant-vs-faiss-vs-pgvector-vector-database-for-local-rag-local-llmn]

### Atomic item: LLM judge cage + human agreement

- G-Eval GPT-4 + CoT Spearman .514 with humans, beating prior reference-free metrics (empirical)
  > "G-EVAL with GPT-4 as the backbone model achieves a Spearman correlation of 0.514 with human on summarization task, outperforming all previous methods by a large margin"
  [scholar record: g-eval-nlg-evaluation-using-gpt-4-with-better-human-alignment-acl-anthology]
- Output-based judges Pearson .81/.68 on code translation/generation, near-human (empirical)
  [scholar record: llm-as-judge SE study 2025]
- Position flips ~35% of GPT-4 pairwise verdicts on order swap (empirical)
  [why-llm-judges-are-biased-position-self-preference]
- Style bias 0.10-0.76 dominates; position ≤0.04 in multi-family controlled study (empirical, Kabir 2026)
  [judging-the-judges-a-systematic-evaluation-of-bias-mitigation-strategies-in-llm]
- Self-enhancement bias irreducible under swap debiasing (formal decomposition, SSRN theory)
  [gap-fill/scholar: modern-llm-evaluation-techniques SSRN]
- Best judge human-equivalent on only 4/11 criteria in global-health eval (empirical)
  [scholar record: human-evaluators-vs-llm-as-a-judge 2025]
- Pairwise flips ~35% vs ~9% absolute under distractors; absolute scoring more robust (empirical, 2504.14716)
  [gap-fill cc-4 report: pairwise-or-pointwise-evaluating-feedback-protocols-for-bias-in-llm-based-evalua]
- RAGAS-zero-shot detectors modest (bal-acc <78%, F1 <72%); HHEM-2.1 competitive but far from parity; human-pooled FaithJudge 84%/82.1% (empirical, Vectara EMNLP-2025)
  [gap-fill cc-4 report: benchmarking-llm-faithfulness-in-rag-with-evolving-leaderboards]
- Mid-tier + right debias beats frontier at 15× lower cost (71.0%, κ=0.549, ~$0.001/eval) (empirical)
  [judging-the-judges-a-systematic-evaluation-of-bias-mitigation-strategies-in-llm]
- MT-Bench 80% agreement is aggregate, not per-task production guarantee (methodological warning)
  [llm-evaluation-frameworks-compared-how-to-actually-measure-what-your-model-does]

### Atomic item: escalation / selective prediction

- Calibrators improve risk-coverage AUC 6-16% over MaxProb in IID and OOD (empirical, Varshney repl4nlp)
  [200809371-towards-improving-selective-prediction-ability-of-nlp-systems]
- Temperature scaling cuts ECE ~31% (0.0051→0.0035) without accuracy loss (empirical)
  [gap-fill/scholar: reliability-aware BERT emotion classification 2026]
- AUGRC supersedes AURC; rankings change on 5/6 datasets (formal + benchmark, Traub NeurIPS-2024)
  [gap-fill cc-5 report: 240701032-overcoming-common-flaws-in-the-evaluation-of-selective-classification]
- UniCR learned calibration head + conformal risk control beats thresholds under shift (empirical 2025)
  [gap-fill cc-5 report: 250901455-trusted-uncertainty-in-large-language-models-a-unified-framework-for-c]
- ACI single-parameter online update gives provable long-run coverage under arbitrary drift (formal, Gibbs & Candès 2021)
  [gap-fill cc-5 report: 210600170-adaptive-conformal-inference-under-distribution-shift]
- 94% of correct predictions abstained on at 10% risk (BLIP2/A-OKVQA); recovery +20pp coverage without raising risk at 20% tolerance (empirical, ReCoVERR)
  [selective-selective-prediction-reducing-unnecessary-abstention-in-vision-languag]
- Defer-only handoff (no suppressed draft shown) improves downstream human accuracy vs showing the guess (empirical, Bondi 2021)
  [selective-prediction-tasks]
- Post-abstention re-attempting lifts coverage ~80% without accuracy drop; risk improvements up to 21.81 IID / 24.23 OOD (empirical)
  [scholar record: post-abstention ACL-2023]

### Atomic item: golden set / agreement gates

- N=200 ≈ nominal bootstrap coverage; N=100 inadequate (simulation, Zapf 2016)
  [gap-fill cc-6 report: measuring-inter-rater-reliability-for-nominal-data-which-coefficients-and-confid]
- Customary bootstrap under-dispersed at small n/high α; analytical jackknife preferred (methodological, Hughes 2022)
  [gap-fill cc-6 report: 221013265-toward-improved-inference-for-krippendorffs-alpha-agreement-coefficien]
- Krippendorff benchmarks: ≥0.80 reliable, 0.667-0.80 tentative, <0.667 block (canonical)
  [gap-fill cc-6 report: krippendorffs-alpha-intercoder-reliability-casrai]
- Author-labeled Twitter sarcasm: third-party pairwise κ 0.36-0.39; 30% sarcastic missed, 45% perceived-sarcastic not intended (empirical, iSarcasm ACL-2020)
  [gap-fill cc-6 report: isarcasm-a-dataset-of-intended-sarcasm]
- CI on alpha spans ~0.05-0.10 even with hundreds of items — scores are bands (practice)
  [interim-golden-set-adjudication-and-agreement-gate]

### Atomic item: data foundation / brand selection / leakage

- Exact-corpus EDA: AmazonHelp 169,840 tweets/168,823 responses; AppleSupport 106,860/106,648; median response TMobileHelp 2.75min, AmericanAir 10.73, AmazonHelp 11.47 vs AppleSupport 70.97, British_Airways 180.5 (measured EDA)
  [gap-fill cc-1 report: github-abh2050customer_support_intelligence]
- 1,537,843 inbound tweets after filtering (~55% of ~2.8M); 7-category routing precedent; TF-IDF vs DistilBERT on 1.5M (precedent)
  [gap-fill cc-1 report: github-vishesh062customer-support-tweet-classifier]
- TNE-AI conversation derivative: 794k rows, 109 companies, threaded (dataset fact)
  [tne-aicustomer-support-on-twitter-conversation-datasets-at-hugging-face]
- Workspace forensics: pool lacks thread/time keys; 200/200 golden texts verbatim in train pool; same-thread target-in-KB unauditable; virgin_threads.parquet already has thread_id/created_at/gap_split (measured, interim leakage note)
  [interim-leakage-safe-temporal-split-vs-random-stratified-split]
- IID→OOD degradation is the norm; golden should BE the OOD slice (Varshney selective-QA under shift: calibrated abstention answers 56% at 80% accuracy vs 48% for raw probabilities)
  [scholar record: selective QA under domain shift 2020]

### Atomic item: architecture minimalism / security / harness

- LangChain v1.0 stable Oct 2025, 126k+ stars, 500+ integrations; earns overhead only for multi-step agent workflows with tool loops (vendor-adjacent explainer, read in full)
  [rag-vs-langchain-which-do-you-need]
- Plain Python + direct APIs faster to build/debug/maintain for simple RAG (practitioner consensus, 4 sources)
  [is-langchain-becoming-too-complexbloated-for-simple-rag-applications-in-2025-co]
- PII redaction + prompt-injection guardrails + escalation paths required; support prompts otherwise leak (practice consensus, 4 sources)
  [safety-and-pii-in-customer-support-redaction-refusals-and-escalation-paths-for-p]
- Langfuse hosted parity real: versioned datasets + experiment runner + RegressionError + GitHub-Action CI (official docs)
  [gap-fill cc-4 report: experiments-in-cicd-langfuse]
- Polars + DuckDB 10-100× pandas on multi-million-row ETL without distributed systems (tutorial benchmark)
  [python-data-pipelines-with-polars-and-duckdb-andrew-odendaal]

### Contested pairs (top-5 from contradiction graph, both sides)

1. intent-classifier-choice: SetFit-first+routing vs native-LLM — see classifier bullets above; resolution: conditional SetFit-first.
2. judge-trust: caged-judge-headline vs human-only — see judge bullets; resolution: caged judge behind tiered gates.
3. retrieval-hybrid-vs-pure: hybrid-default vs dense-sufficiency — see retrieval bullets; resolution: hybrid gated on ≥5pt identifier gain.
4. taxonomy-size: 6-8 data-derived vs 77-preset — OOS-collapse + annotation-math vs benchmark-reuse; resolution: small, Banking77 intent-work-only.
5. escalation-threshold: calibrated-threshold vs learned-module — MaxProb-non-dominance vs conditional calibrator gains + UniCR; resolution: MaxProb floor, challenger contest on AUGRC.
