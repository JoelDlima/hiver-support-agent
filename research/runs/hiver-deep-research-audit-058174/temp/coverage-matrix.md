## Coverage Matrix — query phrase → atomic item mapping

| Query phrase (verbatim) | Mapped atomic item(s) | Scope check | Gap? |
|---|---|---|---|
| "An AI coding agent has already implemented a substantial version" | Entity: Existing Hiver workspace implementation | OK — full scope (audit target, not assumed good/bad) | No |
| "RESEARCH → INSPECT → AUDIT → BENCHMARK → IDENTIFY WEAKNESSES → RESEARCH ALTERNATIVES → RE-ARCHITECT ... → VALIDATE → DOCUMENT" | Sub-Q1 (per-layer criticism w/ evidence); scope: re-engineering sequence | OK — all ten verbs covered | No |
| "Customer Support on Twitter" + "thoughtvector/customer-support-on-twitter" | Entity: Customer Support on Twitter dataset | OK — structure, reconstruction, threads, noise | No |
| "PolyAI/banking77" + "intent work ONLY" | Entity: Banking77; scope condition on its restricted role | OK — full scope incl. transferability limits | No |
| "Pick ONE brand" | Sub-Q2 (brand selection); Entity: Selected brand | OK — quality-maximizing, not row-count | No |
| "Classify each incoming customer message into a small set of intents that you define from the data" | Sub-Q3 (taxonomy derivation) | OK — data-derived, small, distinguishable | No |
| "Draft a reply grounded in how that brand has historically resolved similar issues" | Sub-Q7 (retrieval of problems WITH resolutions); reply grounding | OK — similar-problem+resolution, not similar-wording | No |
| "Decide whether the message should be auto-handled or escalated ... with a stated reason" | Sub-Q10 (calibrated escalation + reason) | OK — signals, calibration, coverage-vs-quality | No |
| "convince us the agent is good enough to trust" / "PROVE IT WORKS" | Sub-Q16 (trust over LLM wrapper); eval methodology | OK — proof over marketing | No |
| "150–250 hand-labelled examples" + "sampling" + "labelling" + "label scheme" | Sub-Q5; Entity: Golden set | OK — stratification, difficulty, holdout, hard negatives | No |
| "Automated metrics" + "LLM-as-judge rubric" + "how well the LLM judge agrees with a human" | Sub-Q11; Entity: LLM-judge + human agreement | OK — rubric, agreement metrics, disagreements | No |
| "Maximum 6 pages" + 21-item report structure | required_section_headings 1–21; response_format structured | OK — all 21 headings in prompt order | No |
| "one trivial baseline" + "one simple baseline" | Sub-Q6; Entity: Baselines | OK — honest, non-strawman baselines | No |
| "top 5 failure modes with real examples" + "hypotheses" | Sub-Q12 | OK — real outputs, root causes, mitigation status | No |
| "What is misleading about my headline number?" | Sub-Q13 (mandatory honesty section) | OK — dedicated heading 17 | No |
| "what would be done with one additional week" | Sub-Q14 (heading 20) | OK | No |
| "10–15 non-obvious decisions" | Entity: decision log (heading 21) + technology-decisions/ | OK | No |
| "train/test conversation overlap" / "temporal leakage" / "retrieval of the target response" / "golden-set contamination" | Sub-Q4 (leakage-proof split) | OK — all four leakage classes named | No |
| "accuracy / macro F1 / per-class precision/recall / confusion matrix" | Evaluation methodology (heading 11) | OK — intent eval independent | No |
| "AUTOMATION COVERAGE vs QUALITY curves" | Sub-Q10 calibration | OK | No |
| "correlation / agreement rate / rank correlation / disagreement" | Sub-Q11 human agreement | OK | No |
| Data / ML-AI / Retrieval / Agent / Backend / Database / Evaluation / Frontend / Infra / Scalability audit layers | Sub-Q1 per-layer; entities across stack | OK — every named layer mapped | No |
| "pandas / Polars / DuckDB / Arrow / Parquet / Spark / Dask" | Entity: Data engineering stack | OK — full list preserved | No |
| "PostgreSQL / pgvector / SQLite / DuckDB / Elasticsearch / OpenSearch / Qdrant / Weaviate / Milvus / Pinecone / FAISS / Chroma / LanceDB / Redis / graph databases" | Entity: Storage layer | OK — full list preserved | No |
| "classical classifiers / transformer classifiers / embeddings / fine-tuning / LoRA / PEFT / zero-shot / few-shot / clustering / topic modelling" | Evaluation/architecture sub-questions | OK — ML capability covered | No |
| "OpenAI / Anthropic / Google / open-weight / local / inference providers / reasoning / small / routers" | Entity: LLM options; Sub-Q8 | OK — no assumed winner | No |
| "LangGraph / LangChain / LlamaIndex / PydanticAI / OpenAI Agents SDK / Google ADK / Microsoft Agent Framework / CrewAI / DSPy / Mastra / Agno / Strands / Vercel AI SDK" + "whether NO agent framework is better" | Entity: Agent frameworks; Sub-Q9 | OK — includes none-option | No |
| "RAGAS / DeepEval / LangSmith / Langfuse / Braintrust / promptfoo" + "pairwise / rubric / calibration / abstention" | Entity: Eval tooling; Sub-Q11 | OK | No |
| "OpenTelemetry / Phoenix / MLflow" | Entity: Eval/observability tooling | OK | No |
| "Docker / serverless / inference servers / caching / queues / workers" | Entity: Deployment/infrastructure | OK | No |
| "prompt injection / PII / secrets / validation" | Entity: Security/privacy | OK | No |
| "unit / integration / regression / load / adversarial / synthetic / human" testing | Evaluation methodology | OK — testing approaches covered | No |
| "reproduce headline results in under 15 minutes" + "subsample" | Scope condition (fast subsample); reproducibility | OK | No |
| "THE SIMPLEST ARCHITECTURE THAT ACHIEVES THE REQUIRED QUALITY" | Scope: minimum-complexity principle | OK | No |
| "Never fabricate ... NOT MEASURED or ESTIMATED" | Scope: honesty constraint | OK | No |
| "Architecture A/B/C/D/E" comparison | Sub-Q15 (technology winners) + heading 5 | OK — evidence-selected, not forced | No |
| "research/..." artifact tree + "research_log.md" + "technology-decisions/" | required_formats | OK | No |
| "September 14, 2026" + "last 1–2 years" | time_horizons | OK — as-of verification date | No |
| MCP tools (context7, exa, fetch, filesystem/git, github, hyperresearch, open-websearch, sequential-thinking, time) | Wrapper requirements in scaffold.md (usage strategy, not report content) | OK — correctly kept out of decomposition per step-1 rule 6 | No |
