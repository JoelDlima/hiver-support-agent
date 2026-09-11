# Research Log

## 2026-09-10 — Agent 4 (Retrieval Research)
- Task: grounded-reply retrieval over AppleSupport history (~100k), local/CPU, <15 min repro, no managed vector-DB cost.
- Measured corpus: `data/raw/twcs.csv` = 2,811,774 rows, 106,860 outbound AppleSupport replies; mean reply ~119 chars.
- Ran 11 web searches (BM25 vs dense vs hybrid 2025–2026; FAISS/Chroma/LanceDB/pgvector/Elasticsearch incl. Sep-2026 maintenance; tweet chunking; query expansion/HyDE; cross-encoder rerank; RAG eval metrics; RRF; sklearn BM25).
- Built repro `scripts/build_retrieval_baseline.py` (sklearn-only): 106,860 docs indexed in 17.1 s total, p50 34.6 ms / p95 38.1 ms, ~44 MB in `data/indexes/` (`tfidf_vectorizer.pkl`, `tfidf_matrix.npz`, `nn_index.pkl`, `doc_ids.csv`, `index_meta.json`).
- Wrote `research/retrieval/retrieval_analysis.md` (options table + pipeline + eval gates).
- RECOMMENDATION: no vector DB; ship TF-IDF/BM25 + MiniLM-L6-v2 hybrid (RRF, top-k=5, cross-encoder rerank, tweet_id citations), files in `data/indexes`. Next: build MiniLM arm + RRF + reranker; HyDE deferred.
