# Research index (Hiver AppleSupport)

- `problem/problem_decomposition.md` — objective, I/O, intents (11), escalation 4-trigger, success bars
- `competitors/analysis.md` — 16 solutions, differentiation (hybrid+validate+eval rigor)
- `models/model_comparison.md` — TFIDF-LogReg vs MiniLM/BERT vs gpt-4o-mini; cheapest split wins
- `retrieval/retrieval_analysis.md` — no vector DB; TF-IDF NN 17s/p50 35ms, top-5 + IDs
- `agents/orchestration.md` — no agent framework; deterministic + Pydantic
- `datasets/data_quality.md` — 2.8M scan, Apple 204k union, 11 intents, preprocessing
- `open_source/ecosystem.md` + `requirements.txt` — CPU-only stack
- `papers/academic_review.md` — Banking77, SetFit, RAG faithfulness, judge κ (75-pair protocol)
- `evaluation/eval_strategy.md` + `../../evaluation/rubric.md` — dual golden, κ gates, F1–F8
- `infrastructure/production.md` + `../../deployment/Dockerfile.simple` — stateless FastAPI, LRU, costs
- `architecture/architecture_decision.md` — per-component evidence table
- `../technology-landscape.md` — by capability
- `research_log.md` — DATE/QUERY/SOURCE/FINDING/RELEVANCE/IMPACT (all tracks)

Honesty: estimates labeled, unverified boards flagged, weak-label circularity disclosed. No fake citations.
