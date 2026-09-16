# Retrieval Analysis — Grounded Replies from AppleSupport History (Hiver)

Agent 4 — Retrieval Research. Date: 2026-09-10. Constraint: local/CPU, <15 min repro, no managed vector-DB cost.

## 1. Corpus facts (measured on `data\raw\twcs.csv`, not assumed)

- 2,811,774 rows; 1,537,843 inbound / 1,273,931 outbound; **106,860 outbound `AppleSupport` replies** (~100k target confirmed).
- Reply length (sample.csv, n=93): mean ~119 chars, max 170 chars. Tweets are already atomic — see §4.
- Schema per row: `tweet_id, author_id, inbound, created_at, text, response_tweet_id, in_response_to_tweet_id` — thread linkage is free via `in_response_to_tweet_id` / `response_tweet_id`.

## 2. Evidence base (11 web searches, Sep 2026)

1. **BM25 vs dense vs hybrid 2025–2026:** hybrid + rerank is the consistent winner (Recall@5 0.816, MRR@3 0.605 on 23k financial-QA queries, Akarsu et al. arXiv:2604.01733, Apr 2026); BM25 alone beats dense on precise/lexical corpora (financial docs; CUAD where dense saw only first ~2k chars); hybrid nDCG@10 52.59 vs BM25 43.42 on BEIR; at 512k-doc scale BM25 remained the most robust single retriever ("BM25 Wins at Scale", arXiv:2607.26497). Takeaway: neither signal dominates everywhere — fuse them.
2. **FAISS vs Chroma vs LanceDB vs pgvector vs Elasticsearch (2026 guides):** consensus default = pgvector if Postgres already in stack (good to ~50M vectors); Qdrant for latency-sensitive scale; Chroma for throwaway prototypes; LanceDB for embedded/edge file-based; Elasticsearch 8.18+/9.x (current **9.4.6, Sep 2 2026**) when hybrid lexical+vector in one engine is the requirement. At <1M vectors all guides agree a dedicated server is unnecessary.
3. **Chunking for short texts:** 2025–2026 guides converge on document-based chunking for support tickets — one ticket = one chunk (Amir Teymoori guide; Redis chunking guide). Fixed-size/semantic splitting is for long docs; it only adds cost and boundary errors on tweets.
4. **Query expansion (HyDE/multi-query):** helps sparse/ambiguous queries (Haystack cookbook updated Jul 2026; Multi-HyDE FinNLP 2025) but adds 40%+ latency (HyDE 13.2s vs 7.7s RAG on 1B models) and gives limited benefit on precise queries (arXiv:2604.01733). Verdict: optional stage-2 upgrade, not day-1.
5. **Reranking:** cross-encoders give +30–40% over bi-encoder-only (Agentset leaderboard, Jul 2026); `cross-encoder/ms-marco-MiniLM-L-6-v2` (22M params, 85 MB) does ~1,800 docs/s / ~50 ms per 100 pairs on CPU — fits budget. Rerank only the fused top-k, never the corpus.
6. **RAG eval:** retrieval = Recall@k / MRR / nDCG@k / MAP (+ Hit@k); generation = RAGAS faithfulness, answer relevancy, context precision/recall; TRULENS-style triad. Proposed gates in §6.
7. **Maintenance status (checked Sep 2026):** FAISS active (Meta, v1.12.0 Aug 2025, ~40.8k stars, baseline inside OpenSearch/Milvus); Chroma active (release Aug 21 2026) but issue backlog incl. open security items (CVE-2026-45830/45832 follow-ups); LanceDB active (0.20+, OSS + Enterprise, docs live); pgvector active (0.8/0.9, ships by default in Supabase/Neon/Aurora); Elasticsearch active (9.4.6 Sep 2026). `all-MiniLM-L6-v2` stable (384-d, 90.9 MB, Apache-2.0, truncation at 256 word-pieces — fine for tweets). `rank-bm25`/`BM25S` (numpy/scipy-only, up to 500× faster than rank-bm25) maintained.
8. **RRF fusion:** rank-only fusion `score = Σ 1/(60 + rank)` (Cormack et al. SIGIR'09); Elasticsearch/OpenSearch ship it natively (weighted RRF added 2025); avoids calibrating incomparable BM25 vs cosine scales. k=60 convention, N=50–100 per arm.
9. **TF-IDF/BM25 on short docs:** BM25 remains a strong baseline incl. on tweets (Kadhim 2019: TF-IDF F1 89.77 vs BM25 89.16 on Twitter — near-tie); sklearn-compatible BM25 vectorizers exist (`bm25_vectorizer`, `BM25-scikit-learn`).

## 3. Options table

| Option | Repro / ops | Cost | Fit for 107k short replies | Verdict |
|---|---|---|---|---|
| **TF-IDF/BM25 (sklearn) + sklearn NN, files in `data/indexes`** | Zero new deps, 17 s repro (§5) | $0 | Exact-match strong on templated replies; 35 ms p50 | **Baseline — adopt now** |
| + MiniLM-L6-v2 dense arm, RRF fuse | `pip install sentence-transformers faiss-cpu`, CPU encode ~107k×~1–2 ms | $0 | Covers paraphrase ("battery dies" vs "power drain") | **Adopt as hybrid arm (recommended)** |
| FAISS-cpu flat/IP index file | Same pip line, no server | $0 | Drop-in ANN if corpus grows 10–100× | Defer until >1M docs or latency gate fails |
| Chroma (embedded) | Extra dep + server/embedded process | $0 license, ops cost | Prototype-grade; security backlog open | Reject for now |
| LanceDB (embedded) | Extra dep, Arrow/S3 story | $0 license, ops cost | Pays off for multimodal/edge, not text tweets | Reject for now |
| pgvector / Elasticsearch | New stateful service | Infra + ops | Justified at multi-million scale or multi-tenant search product | Reject for now |
| Pinecone / Qdrant-cloud | Managed service, API keys, egress | Recurring $ | Banned by constraints; zero accuracy need at this scale | **Reject (cost/complexity)** |

## 4. Recommended pipeline

1. **Clean:** lowercase; replace URLs → `url`, handles → `user`; keep emoji/punctuation light-touch (they carry intent). Preserve `tweet_id`, `created_at`, `in_response_to_tweet_id`.
2. **Chunk = one outbound AppleSupport tweet; attach thread context:** prepend the inbound customer tweet it answers (`in_response_to_tweet_id`) as `context` field. No fixed-size splitting (corpus mean 119 chars; splitting destroys the unit).
3. **Metadata pre-filter by intent** (cheap keyword/intent tagger: billing, battery, password/AppleID, update/install, connectivity, hardware) to shrink candidate pool before scoring.
4. **Hybrid retrieve:** (a) BM25/TF-IDF arm (n-gram 1–2, sublinear TF, k=50); (b) dense arm `all-MiniLM-L6-v2` 384-d cosine (k=50); **fuse with RRF (k=60)**.
5. **Shortlist top-k=5** after fusion.
6. **Rerank top-5:** `cross-encoder/ms-marco-MiniLM-L-6-v2`; offline/air-gapped fallback = IDF-weighted bigram-overlap heuristic (deterministic, no weights download).
7. **Generate with citations:** answer must quote/cite `tweet_id`(s); every claim traceable to a retrieved reply (faithfulness gate §6).
8. **Persist:** `data\indexes\` — `tfidf_vectorizer.pkl`, `tfidf_matrix.npz`, `nn_index.pkl`, `doc_ids.csv`, `index_meta.json` (+ later `minilm_embeddings.npy` / `faiss_flat.ip`). Rebuild via `scripts\build_retrieval_baseline.py`.

## 5. Proof a vector DB is not needed (measured, this machine, CPU-only)

`scripts\build_retrieval_baseline.py` on the full 106,860 AppleSupport replies, deps = pandas + scikit-learn + scipy only:

- Load + clean: 11.9 s; TF-IDF (106,860 × 42,675) fit + NN index: **2.8 s**; **total 17.1 s** (limit: 900 s).
- Query latency (20 probes): **p50 34.6 ms, p95 38.1 ms**.
- Index size on disk: ~44 MB (npz 16.3 MB + NN pickle 24.8 MB + vectorizer 1.8 MB + ids 1.6 MB).
- Sanity: query "my iphone battery dies quickly after ios update" returns 5 battery-support replies with `tweet_id` citations, cosine dist 0.674–0.691.

Scaling headroom: brute-force cosine over 107k×384-d MiniLM vectors is ~40M flops/query (~ms on CPU); IVF/FAISS only matters past ~1M docs. Conclusion: managed vector DB buys nothing at this scale — it adds cost, network hops, and a second system to operate.

## 6. Eval gates (before shipping hybrid)

- Retrieval (labeled query set, ≥100 queries): Recall@5 ≥ 0.80, MRR ≥ 0.65, nDCG@5 reported; ablation BM25-only vs dense-only vs RRF must show fusion ≥ best single arm.
- Generation: RAGAS faithfulness ≥ 0.85, answer relevancy ≥ 0.80; zero uncited claims.
- Ops: p95 query latency < 200 ms CPU; full rebuild < 15 min; artifacts committed to `data/indexes` with `index_meta.json`.

## 7. Risks / next steps

- MiniLM arm + RRF + reranker not yet built — owner: next retrieval ticket; all CPU-local, no new infra.
- Query expansion (HyDE/multi-query) deferred: re-evaluate only if paraphrase-heavy queries fail gates.
- If corpus grows >1M docs or p95 breaches 200 ms: swap sklearn NN → `faiss-cpu` IVF/HNSW file index (same `data/indexes` contract).

## Recommendation

**No vector database. Ship TF-IDF/BM25 + MiniLM dense hybrid (RRF-fused, top-k=5, cross-encoder rerank, `tweet_id` citations), persisted as local files in `data\indexes`.** Proven today: full-corpus repro in 17 s on CPU for $0.
