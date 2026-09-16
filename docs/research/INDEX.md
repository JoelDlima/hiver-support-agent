# Research index

The research trail behind the agent: what was read, what was measured, and which
technology choices survived. VirginTrains is the primary brand; the AppleSupport
material is retained as v1 evidence and transfer proof.

- `problem/problem_decomposition.md` — objective, I/O, intents, escalation triggers, success bars
- `competitors/analysis.md` — competing solutions and where this one differentiates (hybrid + validate + eval rigor)
- `competitors/same_brief_scan.md` — scan of publicly visible takes on the same brief
- `models/model_comparison.md` — TF-IDF+LogReg vs MiniLM/BERT vs hosted LLM; cheapest split that wins
- `models/groq_qwen_integration.md` — drafter integration notes, failure modes, validation gate
- `retrieval/retrieval_analysis.md` — no vector DB; TF-IDF NN, latency, top-k + passage IDs
- `retrieval/research_log.md` — retrieval-specific research log
- `agents/orchestration.md` — no agent framework; deterministic pipeline + Pydantic
- `datasets/data_quality.md` — TWCS scan and preprocessing
- `datasets/virgin_data_quality.md` — VirginTrains union scan (primary brand)
- `open_source/ecosystem.md` — CPU-only stack survey
- `papers/academic_review.md` — Banking77, SetFit, RAG faithfulness, judge-kappa protocol
- `evaluation/eval_strategy.md` — golden design, agreement gates, failure taxonomy (see also `../../evaluation/rubric.md`)
- `infrastructure/production.md` — stateless FastAPI, caching, cost envelope (see also `../../deployment/Dockerfile.simple`)
- `architecture/architecture_decision.md` — per-component evidence table
- `technology-decisions/` — ADR-style writeups per technology choice (`MATRIX.md` summarizes)
- `technology-landscape.md` — the same ground organised by capability
- `notes/` — one digest per source read (papers, docs, engineering posts)
- `research_log.md` — DATE / QUERY / SOURCE / FINDING / RELEVANCE / IMPACT across all tracks

Honesty notes: estimates are labelled as estimates, unverified claims are flagged,
weak-label circularity is disclosed in the evaluation writeups, and no citations
are invented.
