## Coverage Report — hiver-support-agent-audit-6d951f (Step 2.5)

70 substantive notes tagged (target 55–80). Zero retracted. Escalation queue empty.

| Atomic item | Status | Sources (count) |
|---|---|---|
| Twitter dataset structure / conversation graph | Well-covered (5) | kaggle-hub mirror notes, HF 945k, TNE-AI conversation variant, amruta33 corpus, papersgraph/openbigdata mirrors, jessica1438 analysis |
| Brand candidates / response patterns | Adequate (3) | dataset mirrors with brand stats, TNE-AI conversation threading, textual-analysis repo |
| Data engineering (pandas/Polars/DuckDB) | Adequate (2) | TDS polars+duckdb tutorial, andrewodendaal pipelines |
| Leakage / temporal splits | Adequate (3) | OOD survey abs, selective-prediction IID/OOD findings, emergentmind selective-prediction topics |
| Intent taxonomy / clustering | Well-covered (5) | BERTopic docs, rohan-paul case study, vps-ticket clustering, IntentBERT, GPT data-augmentation |
| Banking77 + few-shot | Well-covered (6) | Banking77 HF card, Breaking-Bank abs, LLM-Penny article, SetFit repo/blog/paper-abs, intent-in-LLM-age |
| Retrieval lexical/dense/hybrid/rerank | Well-covered (8) | tianpan, mbrenndoerfer fusion, appscale, denser.ai, turion, ES hybrid, contextual-retrieval (Anthropic), vector-db-benchmark |
| Storage / vector DBs | Well-covered (6) | local-llm compare, pythonbook compare, vector-db-benchmark, LanceDB, pgvector, FAISS wiki |
| LLM selection / structured outputs | Adequate (3) | intent-in-LLM-age (SetFit-routing hybrid), LLM-Penny cost study, DSPy framework |
| Agent frameworks vs none | Well-covered (4) | gh-discussion LangChain-bloat, TDS beyond-LangChain, dev.to rebuild, rag-vs-langchain, pipeline-vs-agentic RAG (failed Medium — covered by others) |
| Eval frameworks | Well-covered (7) | adaptiverecall, genai.qa, MLM, agentscamp, knovo, inferencenet, RAGAS repo, promptfoo intro, Langfuse eval |
| LLM-judge validity + bias | Well-covered (9) | G-Eval ACL page, judge survey abs, ai-tldr biases+pitfalls, self-preference arxiv, judging-judges, EMNLP self-preference, bestaiweb limits |
| Escalation / selective prediction / abstention | Well-covered (8) | Art-of-Abstention ACL, repl4nlp calibrator abs, findings-acl.158, TACL abstention survey abs, ReCoVERR html, selective-prediction toolkit, emergentmind ×2, SelectLLM (failed 403 — covered) |
| Human agreement / annotation | Well-covered (4) | mbrenndoerfer IAA, koji guide, datavlab guide, consensus arxiv html |
| Security / PII / prompt injection | Well-covered (4) | cobbai, orchestrator.dev, modelmetry, kommunicate |
| Baselines / headline-metric honesty | Adequate (2) | LLM-Penny error analysis, MLM judge-bias design note |

### Genuine gaps (flagged for drafter)
- Direct PDF full-text for G-Eval/selective-prediction papers: only abstract/landing pages fetched (PDF extractor failed on binary). Mitigated by scholar abstracts (rich) + secondary coverage (toolkit, surveys, ReCoVERR). No locus may anchor a verbatim claim on these PDFs beyond what the landing page + abstract states.
- Kaggle dataset page itself (JS-walled): covered by 3 mirrors + analysis repo.
- Medium-walled pieces (selective-prediction explainer, agentic-RAG): covered by equivalent fetched sources.
- `time_periods` empty — no period-pinned primary-source searches required.

### Redundancy audit (Step 2.6)
Skipped: no claims-*.json files in run temp (fetchers write notes directly). Derivative risk noted: eval-framework comparisons (6 domains) overlap heavily — treated as one independent position (code-first harness + custom rubric beats hosted suites for this assignment), corroborated by MLM + RAGAS/DSPy repos.
