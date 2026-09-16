# 001 — Vector Database Decision (Hiver AppleSupport)

Date: 2026-09-10 | Owner: Swarm B | Status: FINAL v1
Base: `docs/research/retrieval/retrieval_analysis.md` + DDG verification 2026-09-10 (§7 freshness)

## Context
Corpus = 106,860 outbound AppleSupport replies (measured on `data/raw/twcs.csv`, 2.8M rows).
Mean reply ~119 chars — tweets are atomic. Constraint: CPU-only, <$15min repro, $0 infra, no
managed service. Retrieval feeds grounded-reply drafting with `tweet_id` citations.

## Candidates
TF-IDF/BM25 + sklearn NN (file-backed) | + MiniLM-L6-v2 dense arm w/ RRF | FAISS-cpu flat/IVF file |
Chroma (embedded) | LanceDB (embedded) | pgvector (Postgres ext) | Elasticsearch 9.x |
Pinecone / Qdrant-cloud (managed)

## Evidence (VERIFIED vs ESTIMATE)
- VERIFIED (local measure, this machine): TF-IDF 106,860×42,675 fit + NN index = 2.8 s,
  total 17.1 s; p50 34.6 ms / p95 38.1 ms (20 probes); ~44 MB on disk
  (`scripts/build_retrieval_baseline.py`). Source: `retrieval_analysis.md` §5.
- VERIFIED (official, Sep 2026): FAISS latest = **v1.15.0 (2026-07-31)**, faiss-cpu 1.15.0
  on PyPI Aug 03 2026; v1.14.3 Jun 2026; v1.12.0 Aug 2025. MIT license, ~40.9k stars.
  Sources: github.com/facebookdocs/research/faiss/releases (webfetch 2026-09-10),
  PyPI faiss-cpu page, Wikipedia FAISS (stable v1.12.0 / Aug 12 2025 — stale snapshot).
  CORRECTION: `retrieval_analysis.md` §19 cites v1.12.0 — correct as Aug-2025 release,
  but 3 releases behind as of Sep 2026. Decision unaffected (no FAISS needed at this scale).
- VERIFIED (2026 guides, websearch): consensus default = pgvector if Postgres already in
  stack (good to ~50M vectors — Layerbase Aug 2026; gigagpu Apr 2026); Qdrant for
  latency-sensitive scale; Chroma = throwaway prototypes; LanceDB = embedded/edge file;
  ES 9.4.6 (Sep 2 2026) when hybrid lexical+vector in one engine is required.
  At <1M vectors all guides agree a dedicated server is unnecessary.
  Sources: zilliz.com/comparison/faiss-vs-pgvector, layerbase.com (2026-08-25),
  gigagpu.com (2026-04-16), localaimaster.com (2026-02-04).
- VERIFIED (benchmarks, ESTIMATE-grade for our corpus): pgvector vs FAISS — FAISS 20–50×
  faster at scale w/ GPU (1M vec: pgvector ~8 ms vs FAISS-GPU ~0.3 ms per gigagpu);
  100M-vector HNSW bench: pgvector recall@10 0.987 / 1,800 QPS / p99 28 ms / $0.08 per 1M
  queries (jhondados/vector-database-benchmark, Jun 2026). Relevance: proves both are
  overkill at 107k — brute-force cosine over 107k×384-d ≈ 40M flops/query (~ms on CPU).
- ESTIMATE: hybrid RRF + rerank +1–3 pts top-k precision; cross-encoder
  `ms-marco-MiniLM-L-6-v2` ~50 ms/100 pairs CPU. Must validate on ≥100 labeled queries.

## Decision
**No vector database. Ship TF-IDF/BM25 + sklearn NN file index in `data/indexes/`
(baseline now); add MiniLM-L6-v2 dense arm + RRF fuse + top-5 + cross-encoder rerank
as Phase-2 upgrade on the same file contract. FAISS-cpu file index only if corpus >1M
docs or p95 >200 ms.**

## Rejected — why
- FAISS-cpu: buys nothing at 107k (brute-force already ms); adds dep + tuning (IVF/HNSW)
  for zero measured gain. Revisit trigger defined, not speculative.
- Chroma: prototype-grade + open security backlog (CVE-2026-45830/45832 follow-ups per
  retrieval track). Reject for serving path.
- LanceDB: Arrow/S3 + multimodal story irrelevant to text tweets.
- pgvector / Elasticsearch: new stateful service (infra + ops + backup) for a workload
  that fits in a 44 MB file. Justified only at multi-million scale / multi-tenant search.
- Pinecone / Qdrant-cloud: recurring $ + API keys + egress + network hops; banned by
  cost constraint; zero accuracy need at this scale.

## Cost / complexity / failure / scale
- Cost: $0 inference + $0 infra (VERIFIED local). Managed alt = recurring $/mo + egress.
- Complexity: zero new deps (pandas+sklearn+scipy); rebuild <15 min; artifacts versioned
  (`tfidf_vectorizer.pkl`, `tfidf_matrix.npz`, `nn_index.pkl`, `doc_ids.csv`,
  `index_meta.json`).
- Failure: empty-retrieval → abstain + escalate (score<0.08); no network dependency →
  no outage class; corrupt index → rebuild offline, `/readyz` version gate.
- Scale: workers=cores → replicas (read-only file per host) → ANN sidecar (faiss-cpu
  IVF/HNSW, same `data/indexes` contract). Triggers: KB >100k→1M docs or FTS p95 >50 ms.
