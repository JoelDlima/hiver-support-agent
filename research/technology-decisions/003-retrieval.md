# 003 — Retrieval Decision (Hiver AppleSupport)

Date: 2026-09-10 | Owner: Swarm B | Status: FINAL v1
Base: `research/retrieval/retrieval_analysis.md` + `research/models/model_comparison.md` §§1.2–1.3

## Context
Ground T2 replies in AppleSupport history (107k replies) + mini-KB (10–30 help snippets).
Requirements: chunk/index/metadata/hybrid/rerank/cite, measured separately (§17);
`tweet_id` citations on every claim; abstain when ungrounded.

## Candidates
TF-IDF/BM25 lexical arm | MiniLM-L6-v2 / e5-small-v2 dense arm | RRF hybrid fusion |
cross-encoder rerank (bge-reranker-base / ms-marco-MiniLM-L-6-v2) | HyDE/multi-query
expansion | 7B embedders (e5-mistral-7B, gte-Qwen2-7B, NV-Embed-v2)

## Evidence (VERIFIED vs ESTIMATE)
- VERIFIED (measured): one outbound tweet = one chunk is correct (mean 119 chars, max 170,
  n=93); thread context attached via `in_response_to_tweet_id` (free linkage).
  Fixed-size/semantic splitting only adds boundary errors on tweets (2025–26 guides).
- VERIFIED (literature, Apr 2026): hybrid+rerank wins (Recall@5 0.816, MRR@3 0.605, 23k
  financial-QA; Akarsu et al. arXiv:2604.01733); BM25 beats dense on precise/lexical
  corpora; BM25 most robust single retriever at 512k-doc scale (arXiv:2607.26497).
  Takeaway: fuse, don't pick one signal.
- VERIFIED (models): `all-MiniLM-L6-v2` 22M/384-d/256-WP/stable/Apache-2.0, ~5× faster
  than MPNet; `e5-small-v2` 33M/384-d/512-tok/MIT (needs `query:`/`passage:` prefixes);
  `rank-bm25`/`BM25S` maintained (numpy/scipy-only, up to 500× faster than rank-bm25).
- ESTIMATE: BM25-only vs dense-only vs RRF ablation must show fusion ≥ best single arm
  (gate: Recall@5 ≥0.80, MRR ≥0.65 on ≥100 labeled queries); rerank +30–40% over
  bi-encoder-only (Agentset Jul 2026), `ms-marco-MiniLM-L-6-v2` ~50 ms/100 pairs CPU.
- ESTIMATE (deferral rationale): HyDE adds 40%+ latency for limited gain on precise
  queries — stage-2 only.

## Decision
**Hybrid: (a) BM25/TF-IDF arm (1–2g, sublinear TF, k=50) + (b) MiniLM-L6-v2 dense arm
(384-d cosine, k=50), RRF-fused (k=60), shortlist top-5, cross-encoder rerank top-5,
`tweet_id` citations. Metadata pre-filter by intent. v1 ships TF-IDF arm (built, 17 s);
dense arm + RRF + reranker is the next retrieval ticket (all CPU-local, same file
contract). Offline fallback: IDF-weighted bigram-overlap heuristic (no weights DL).**

## Rejected — why
- 7B embedders: top MTEB retrieval (nDCG@10 ~65–71 ESTIMATE) but 14–16 GB VRAM, ~100 ms+/q
  ESTIMATE — violates no-large-GPU constraint for no measurable win on 11-class tweets.
- bge-m3 / bge-large as default: 109–568M, multilingual/long-doc strengths irrelevant to
  English 119-char tweets; CPU ~150 ms/q ESTIMATE.
- HyDE/multi-query day-1: latency +40% for paraphrase-only wins; re-evaluate iff
  paraphrase-heavy queries fail gates.
- Fixed-size chunking / semantic splitting: destroys the atomic tweet unit.

## Cost / complexity / failure / scale
- Cost: $0 (CPU encode ~1–2 ms/doc ESTIMATE for 107k MiniLM vectors; brute-force cosine
  ~40M flops/query).
- Complexity: same `data/indexes` contract (+ `minilm_embeddings.npy` / `faiss_flat.ip`
  later); intent pre-filter shrinks candidate pool before scoring.
- Failure: no-retrieval (score<0.08) → abstain + escalate, never invent; poison-passage
  risk → answer-level faithfulness gate (RAGAS ≥0.85), recall@k never substitutes.
- Scale: sklearn NN → faiss-cpu IVF/HNSW file swap past ~1M docs or p95 >200 ms; rerank
  only fused top-k, never corpus.
