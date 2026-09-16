# Technology Audit — D17 (Hiver AppleSupport, Swarm B, 2026-09-10)

Covers D1–D17 discovery: full landscape, no anchor, combos, non-AI, OSS+closed,
prod experiences, pipeline, landscape-by-capability, min-components, measurable-problem,
emergent arch, audit. Evidence: 001–006 + MATRIX.md + per-track docs.

## Considered (full landscape surveyed)
TF-IDF/LogReg · keyword rules · MiniLM-L6-v2 (+GIST) · e5-small-v2 · DistilBERT ·
DeBERTa-v3-small · twitter-roberta · bge-m3 / bge-large / 7B embedders · bge-rerankers /
ms-marco-MiniLM cross-encoder · BM25 variants · HyDE/multi-query · RRF fusion ·
FAISS-cpu · Chroma · LanceDB · pgvector · Elasticsearch 9.x · Pinecone/Qdrant-cloud ·
templates · gpt-4o-mini · haiku-4-5 / 3.5 · Llama-3.x · Mistral-7B/Small · Gemma-2 ·
Gemini-2.0-flash · frontier-large · LangChain/Graph · LlamaIndex · PydanticAI ·
OpenAI Agents SDK · CrewAI · MAF · ADK · DSPy · MCP · FastAPI/uvicorn · SQLite-WAL/FTS5 ·
joblib · LRU/slowapi · Docker-slim · Redis · Postgres · K8s · Celery · sklearn metrics ·
heuristic judge · LLM-judge · RAGAS · BLEU/ROUGE/BERTScore · golden-200 + F1–F8.

## Selected (v1 serving path)
- Intent: TF-IDF+LogReg baseline (mandatory) → MiniLM-L6-v2 + head (primary T1).
- Retrieval: TF-IDF/BM25 + sklearn NN files (`data/indexes/`); chunk = 1 tweet + thread ctx.
- Draft: per-intent templates + `tweet_id` citations (keyless default).
- Escalate: 4-trigger rules (never threshold-only, never model self-delegation).
- Orchestration: plain Python + Pydantic v2 + sklearn (no agent runtime).
- Store/serve: FastAPI ≥0.133 (venv 0.141.1) + uvicorn + joblib + SQLite-WAL RO + LRU-1024.
- Eval: golden-200/60-overlap + deterministic metrics + heuristic judge + F1–F8.

## Rejected — why
| Rejected | Why (one line) |
|---|---|
| FAISS/Chroma/LanceDB/pgvector/ES/managed now | 44 MB file does the job (17 s, p50 35 ms VERIFIED); service adds cost/ops for zero measured gain |
| 7B embedders / bge-m3 default / frontier-large per-req | 5–50× cost/latency/GPU for single-digit gains ESTIMATE; violates CPU-only |
| Haiku-4-5 / mini as v1 default drafter | Cost (4–8×) / key + hallucination surface; templates already 4.75/5 grounded VERIFIED |
| Llama/Mistral/Gemma self-host default | No struct SLA + ops + gated licenses (Llama/Gemma); breaks 15-min repro |
| All agent frameworks as runtimes | Fixed 6-stage workflow; loops add compounding error + 10–50× cost, zero needed feature |
| Postgres / Redis / K8s / Celery / GPU now | Triggers not fired (writes <10/s, DB <1 GB, hit-rate TBD) |
| Launch-on-containment/CSAT/BLEU/recall@k-alone | All mislead in known directions (Kaizo/RAGAS-retEval/Han 2026); banned as proof |

## Not needed — why (explicit non-goals)
- K8s / service mesh / Prometheus stack: single CPU container; `/metrics` JSON suffices.
- GPU (train or serve): encoders + TF-IDF are CPU-ms; LLM optional API, never local large.
- Managed vector DB / second database: no Postgres in stack → pgvector would *create*
  the problem it solves.
- Conversational memory / multi-turn agents: no-history constraint (single-tweet I/O).
- Full LLM fine-tuning (DeepSpeed/vLLM): >15 min, GPU-bound; MiniLM inference is ceiling.
- Gradio primary / second UI: one Streamlit triage dashboard + CLI fallback minimizes deps.
- Spark / feature store / ELK: <100k docs, file-backed, stdout JSON logs.

## Revisit later (trigger-gated, not speculative)
- MiniLM dense arm + RRF + cross-encoder rerank → next retrieval ticket (all CPU-local).
- bge-reranker-base over top-20 → Phase 2, iff KB grows / gates missed.
- gpt-4o-mini gated drafter → Phase 2, behind Pydantic + retry + fallback + spend cap.
- Haiku-4-5 promotion → iff blind A/B delta > retry-adjusted cost delta.
- faiss-cpu IVF/HNSW file index → iff corpus >1M docs or p95 >200 ms.
- HyDE/multi-query → iff paraphrase-heavy queries fail gates.
- DSPy/GEPA offline prompt-opt → iff single-draft quality lags (never as serving runtime).
- llama-index-workflows (routing subgraph only) → iff step order becomes unpredictable AND
  all 4 criteria in 004 §Cost hold.
- Redis / Postgres+pgvector / GPU-vLLM → iff `/metrics` triggers fire (005 §Decision).
- Supervised classifier on 500+ human labels + pinned LLM + NLI gate → week-2 track.
- MAF / Foundry / ADK runtime → iff Hiver standardizes on Azure/GCP agent stack.
- MCP tool exposure → iff exemplar/ticket connector needs standard tooling (≤4 tools).

## Freshness corrections applied (this audit)
1. sklearn: requirements pin 1.7.1 STALE — venv 1.9.0 = latest (Jun 2026); multi_class
   removal = 1.8 (not 1.7, per #31781/#31795); Hiver code safe (no multi_class passed).
2. FastAPI: requirements pin 0.115.12 STALE (Mar 2025) — venv 0.141.1 = latest
   (Jul 2026); CVE-2026-48710 requires ≥0.133. Action: bump pin.
3. FAISS: track cites v1.12.0 (Aug 2025, correct then) — latest v1.15.0 (Jul 2026).
   Decision unchanged.
4. gpt-4o-mini $0.15/$0.60 + structured outputs — CONFIRMED current (no change).
5. pgvector-vs-FAISS guidance — CONFIRMED (50M rule); both unnecessary at 107k.
