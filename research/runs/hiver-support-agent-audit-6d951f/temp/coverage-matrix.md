## Coverage Matrix — query phrase → atomic item mapping

| Query phrase (verbatim) | Mapped atomic item(s) | Scope check | Gap? |
|---|---|---|---|
| "Pick ONE brand from the dataset" | Sub-Q: brand maximizing submission quality; Entity: selected brand | OK — quality criteria, not row count | No |
| "small set of intents that you define from the data" | Sub-Q: taxonomy derived from brand data; Entity: intent taxonomy | OK — data-derived, small, routable | No |
| "Draft a reply grounded in how that brand has historically resolved similar issues" | Sub-Qs: retrieval strategy; reply grounding; similar-problem-vs-similar-wording | OK — full scope | No |
| "auto-handled or escalated to a human — with a stated reason" | Sub-Qs: escalation policy; calibrated threshold; coverage-vs-quality | OK — reason required, not bare binary | No |
| "convince us the agent is good enough to trust" | Sub-Qs: what good means; why trust; advantage over LLM wrapper | OK | No |
| "Customer Support on Twitter ... Approximately 3M tweets/replies, multi-turn threads" | Entity: Twitter dataset; Sub-Q: conversation-graph reconstruction | OK — graph, not independent rows | No |
| "Banking77 ... may be used for intent work ONLY" | Entity: Banking77; scope condition intent-only | OK — constraint preserved | No |
| "Runnable pipeline ... under 15 minutes" | Sub-Q: reproducibility/subsampling | OK | No |
| "Golden evaluation set 150–250 hand-labelled" | Sub-Q: golden sampling + labelling docs | OK — sampling, labelling, scheme rationale | No |
| "Evaluation harness ... LLM-as-judge ... agrees with a human" | Sub-Qs: independent metrics; judge rubric; human agreement | OK | No |
| "Maximum 6 pages ... results vs at least two baselines ... trivial ... simple" | Sub-Q: honest baselines; report contents | OK | No |
| "top 5 failure modes with real examples ... hypotheses" | Sub-Q: failure modes with 7-field structure | OK | No |
| "What is misleading about my headline number?" | Sub-Q: headline critique (mandatory) | OK — not a formality | No |
| "what would be done with one additional week" | Sub-Q: one-week roadmap | OK | No |
| "Decision log 10–15 non-obvious decisions" | Required format: decision log | OK | No |
| "data leakage ... temporal leakage ... retrieval of the target response itself" | Sub-Q: leakage-safe splits; past→future simulation | OK — full leakage family | No |
| "BM25 ... TF-IDF ... vector ... hybrid ... reranking ... knowledge graphs" | Entity: retrieval systems | OK — full scope, no anchoring | No |
| "PostgreSQL ... pgvector ... SQLite ... FAISS ... Chroma ... LanceDB ... Redis" | Entity: storage systems | OK | No |
| "classical classifiers ... transformer ... LoRA ... zero/few-shot ... clustering" | ML capability in architecture Sub-Q | OK | No |
| "OpenAI ... Anthropic ... Google ... open-weight ... routers" | Entity: LLM options, per-component roles | OK | No |
| "LangGraph ... LangChain ... LlamaIndex ... PydanticAI ... DSPy ... NO agent framework" | Entity: agent frameworks + no-framework alternative | OK — both readings covered | No |
| "RAGAS ... DeepEval ... LangSmith ... Langfuse ... Braintrust ... promptfoo ... calibration" | Entity: evaluation stack | OK | No |
| "Docker ... serverless ... caching ... queues" | Sub-Q: deployment/scalability without over-engineering | OK | No |
| "prompt injection ... PII ... secrets ... privacy" | Sub-Q: security/privacy | OK | No |
| "pandas ... Polars ... DuckDB ... Arrow ... Spark" | Sub-Q: data-engineering choices | OK | No |
| "DO NOT BUILD A LANGCHAIN PROJECT ... BUILD THE BEST SOLUTION" | Scope: no technology anchoring; minimum complexity | OK | No |
| "MINIMUM COMPLEXITY ... SIMPLEST ARCHITECTURE" | Sub-Q: minimal architecture maximizing trust/complexity | OK | No |
| "PHASE 1 ... PHASE 14" / "FINAL DELIVERABLES" / "FINAL REPORT" 21 sections | Required section headings 1–10; decision tables; artifacts | OK — compressed without dropping asks | No |
| "If another student had submitted the CURRENT Hiver implementation ... criticize?" | Sub-Q: forensic audit verdict + highest-value fixes | OK | No |
