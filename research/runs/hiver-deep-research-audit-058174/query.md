---
vault_tag: hiver-deep-research-audit-058174
created: 2026-09-14T08:11:00Z
source: user-prompt
---

# HIVER — DEEP RESEARCH + FORENSIC AUDIT + RE-ENGINEERING DIRECTIVE

CURRENT DATE:
September 14, 2026

PROJECT:
Hiver

IMPORTANT:
This is NOT a greenfield project.

An AI coding agent has already implemented a substantial version of this project in the Hiver workspace during a previous session.

DO NOT ASSUME THAT IMPLEMENTATION IS CORRECT.

DO NOT ASSUME THAT THE EXISTING ARCHITECTURE IS GOOD.

DO NOT ASSUME THAT THE CURRENT MODEL, retrieval system, prompts, evaluation, backend, frontend, database, infrastructure, or scalability design are adequate.

Treat the existing implementation as an external team's submission that you have been asked to audit before it is submitted.

Your job is to:

RESEARCH → INSPECT → AUDIT → BENCHMARK → IDENTIFY WEAKNESSES → RESEARCH ALTERNATIVES → RE-ARCHITECT WHERE NECESSARY → IMPLEMENT IMPROVEMENTS → VALIDATE → DOCUMENT

The goal is NOT to preserve existing code.

The goal is to produce the strongest practical submission possible for this assignment.

======================================================================
# OFFICIAL ASSIGNMENT
======================================================================

Hiver SDE Intern — Take-Home Assignment

What we are testing:
whether you can turn a messy real-world dataset into a working AI system and prove it works.

The proof is worth more than the system.

## The problem

You are given real customer-support conversations between customers and brands on Twitter.

Pick ONE brand from the dataset and build an AI support agent for it that can:

1. Classify each incoming customer message into a small set of intents that you define from the data.

2. Draft a reply grounded in how that brand has historically resolved similar issues.

3. Decide whether the message should be auto-handled or escalated to a human — with a stated reason.

You then have to convince us the agent is good enough to trust.

That is the hard part.

## Dataset

Primary:
Customer Support on Twitter
Kaggle:
thoughtvector/customer-support-on-twitter

Approximately 3M tweets/replies, multi-turn threads, dozens of brands.

Real, noisy, and imperfect.

Optional secondary dataset:
Banking77
Hugging Face:
PolyAI/banking77

Approximately 13k queries and 77 labelled intents.

Banking77 may be used for intent work ONLY.

You may use any LLM API or open model.

## Deliverables

### 1. Repository

Runnable pipeline.

README must allow reproduction of headline results in under 15 minutes.

### 2. Golden evaluation set

150–250 hand-labelled examples created by us.

Must include:

- short explanation of sampling
- explanation of labelling
- rationale for the label scheme

### 3. Evaluation harness

Automated metrics.

LLM-as-judge rubric for reply quality.

Evidence showing how well the LLM judge agrees with a human.

### 4. Report

Maximum 6 pages OR equivalent README section.

Must cover:

- problem framing
- what "good" means for this brand
- what was deliberately NOT built
- results vs at least two baselines
- one trivial baseline
- one simple baseline
- top 5 failure modes with real examples
- hypotheses explaining those failures
- mandatory section:
  "What is misleading about my headline number?"
- what would be done with one additional week

### 5. Decision log

10–15 non-obvious decisions.

Plain bullet list is acceptable.

### Submission

Submit through the designated Notion portal (URL in original assignment).

Include repository link and report.

Do not email submissions.

### Rules

AI coding assistants may be used freely.

The candidate must be able to explain and modify their own code live.

Cite anything borrowed.

Borrowing is allowed.

Not knowing what was borrowed is not.

The evaluators will NOT run the code against the full dataset.

A subsample is expected and encouraged.

======================================================================
# PRIMARY OBJECTIVE
======================================================================

Build the strongest submission possible for the EXACT assignment above.

The key phrase is:

"PROVE IT WORKS."

EVALUATION QUALITY > ARCHITECTURE COMPLEXITY

PROOF > MARKETING

MEASURED PERFORMANCE > CLAIMS

RELIABILITY > AI BUZZWORDS

DOMAIN-SPECIFIC QUALITY > GENERIC LLM BEHAVIOR

Do NOT optimize primarily for UI, number of AI technologies, architecture diagrams, or visual polish.

The core question is:

"Would a reasonable reviewer trust this agent to handle customer support for this specific brand, and can we prove why or why not?"

======================================================================
# CRITICAL RULE — EXISTING IMPLEMENTATION IS NOT TRUSTED
======================================================================

The existing Hiver project is a starting point, NOT the answer. Audit for generic architecture, weak intents, bad sampling, data leakage, conversation-reconstruction errors, poor brand selection, weak retrieval, hallucinated replies, poor escalation logic, arbitrary thresholds, invalid evaluation, LLM judge bias, weak baselines, misleading metrics, hardcoded results, fake confidence, overuse of LLMs, unnecessary agents/vector DBs, outdated libraries, fragile APIs, poor reproducibility, excessive complexity, security problems, frontend/backend disconnects, undocumented assumptions.

If the existing implementation is already good, prove that through evidence. If it is weak, change it.

======================================================================
# RESEARCH FIRST (ABRIDGED SCOPE)
======================================================================

Before modifying important architecture, perform deep research using HyperResearch and the MCP ecosystem (context7, exa, fetch, filesystem/git, github, hyperresearch, open-websearch, sequential-thinking, time) where appropriate. Research ~100-200 meaningful queries across the technology landscape below. Verify current documentation as of September 14, 2026. Do NOT anchor on user-mentioned example technologies (LangChain, Pinecone, RAG, agents, OpenAI) — BUILD THE BEST SOLUTION TO THE ASSIGNMENT.

Technology landscape to investigate: data engineering (pandas, Polars, DuckDB, Arrow, Parquet, Spark, Dask); search/retrieval (BM25, TF-IDF, lexical/semantic/vector/hybrid search, reranking, query expansion, metadata filtering, graph retrieval); storage (PostgreSQL+pgvector, SQLite, DuckDB, Elasticsearch, OpenSearch, Qdrant, Weaviate, Milvus, Pinecone, FAISS, Chroma, LanceDB, Redis, graph DBs); ML (classical/transformer classifiers, embeddings, fine-tuning, LoRA/PEFT, zero/few-shot, clustering, topic modelling); LLMs (OpenAI, Anthropic, Google, open-weight, local, inference providers, reasoning/small models, routers); agent/workflow systems (LangGraph, LangChain, LlamaIndex, PydanticAI, OpenAI Agents SDK, Google ADK, Microsoft Agent Framework, CrewAI, DSPy, Mastra, Agno, Strands, Vercel AI SDK — plus whether NO framework is better); evaluation (RAGAS, DeepEval, LangSmith, Langfuse, Braintrust, promptfoo, LLM-as-judge, human agreement, pairwise/rubric evaluation, calibration, abstention); observability (OpenTelemetry, Langfuse, LangSmith, Phoenix, MLflow); deployment (Docker, serverless, managed services, inference servers, caching, queues); security (prompt injection, PII, secrets, validation); testing (unit/integration/regression/load/adversarial, AI evals, human eval).

Also deeply investigate: Customer Support on Twitter dataset structure and conversation reconstruction; BRAND SELECTION (volume, response coverage, thread depth, intent diversity, resolution availability, golden-set sufficiency, escalation opportunities); INTENT TAXONOMY derived from data (clustering/embeddings/topic discovery + manual inspection; small, distinguishable, routable; Banking77 for intent work ONLY); DATA LEAKAGE audit (train/test thread overlap, near-duplicates, temporal/response leakage, retrieval of target response, golden-set contamination); TEMPORAL evaluation (past→future); GOLDEN SET sampling methodology (stratified, temporal holdout, hard negatives; 150-250 examples); HUMAN LABELING documentation; BASELINES (trivial: majority/always-escalate/fixed-response; simple: TF-IDF/BM25/embedding-NN/simple classifier/direct LLM); INTENT evaluation (accuracy, macro F1, per-class P/R, confusion matrix); REPLY grounding in historical resolutions; RETRIEVAL evaluation (BM25/embeddings/hybrid/rerank/thread-aware); ESCALATION policy (calibrated signals, NOT arbitrary threshold) and calibration (precision/recall of auto-handle vs escalate, coverage-vs-quality curves); LLM-AS-JUDGE rubric (correctness, relevance, grounding, usefulness, brand fit, hallucination, tone, escalation) plus HUMAN AGREEMENT evidence (correlation/agreement metrics + disagreement analysis); mandatory "What is misleading about my headline number?" honesty section; top-5 FAILURE ANALYSIS with real examples.

Forensic audit layers: data, ML/AI, retrieval, agent/orchestration (prove agents help or remove them), backend, database, evaluation, frontend (secondary), infrastructure, scalability (fast reproducible subsample, not full 3M rows). Challenge every component; minimum-complexity principle: simplest architecture achieving required quality. Compare several plausible architectures with measurements. No fake results — report NOT MEASURED/ESTIMATED honestly. Reproducibility <15 min via subsample. Security/privacy (PII) review. Performance (latency p50/p95, cost, throughput).

Final re-engineering sequence: inspect → map → weaknesses → research → alternatives → benchmark current → benchmark baselines → design → implement → re-evaluate → failure analysis → security/scalability/repro review → docs → frontend last.

Final deliverables: working app, reproducible pipeline, brand, intent taxonomy, 150-250 golden set + sampling/labelling docs, 2+ baselines, automated eval, LLM judge + human agreement, escalation + reply evaluation, failure analysis, misleading-headline analysis, 10-15 decision log, research + architecture docs, README, reproducible benchmark, security + scalability + version reviews. Final report docs/FINAL_REPORT.md (~6 pages) covering executive summary, framing, brand, intents, architecture, data processing, retrieval, reply, escalation, baselines, eval methodology, golden set, judge, human agreement, results, failures, misleading-number, scalability, limitations, one-more-week, decision log. Closing audit questions: what would a reviewer criticize about the CURRENT implementation, what changes remove those criticisms — then implement highest-value changes. Maximum trustworthiness per unit of complexity. Every WHY (brand, intents, split, golden set, baselines, retrieval, model, escalation, eval, judge, agreement, failures, headline caveats, trust, advantage over LLM wrapper) backed by data/research/experiments/engineering reasoning.

The objective is the strongest possible Hiver submission for this exact assignment as of September 14, 2026.
