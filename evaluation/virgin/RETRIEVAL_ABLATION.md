# Virgin retrieval ablation (workstream A2)

- Slice: `golden_human_200:seed-7:n=60` (fixed 60 rows of golden_human_200, seed 7; read-only, no data files mutated).
- Fixed: classifier + templates (final LogReg); only retrieval varies: depth k=1 vs 5, retriever keyword (BM25 over virgin KB) vs virgin_nn (TF-IDF-NN), thread context 0 vs 2 prior turns.
- Metrics per arm: recall_proxy (lexical token-F1>=0.15 hit — disclosed PROXY, no relevance labels exist), groundedness_mean + >=4 rate (frozen heuristic, same estimator as BASELINE_VS_FINAL.md), support_rate (claim-entailment of the template draft vs arm passages — the retrieval-sensitive signal), context_hit_rate (share where thread context was found), retrieval p50/p95 ms.
- Entailment: heuristic-offline (deterministic; reproduces without a Groq key).
- Source of truth: `POST /eval/retrieval-ablation` (this table is rendered from a live endpoint response).

| arm | recall_proxy | ground_mean | ground>=4 | support_rate | ctx_hit | p50_ms | p95_ms |
|---|---|---|---|---|---|---|---|
| keyword:k=1:ctx=0 | 0.617 | 4.25 | 0.933 | 0.022 | 0.000 | 110.7 | 199.8 |
| keyword:k=1:ctx=2 | 0.750 | 4.25 | 0.933 | 0.039 | 0.467 | 162.2 | 347.9 |
| keyword:k=5:ctx=0 | 0.883 | 4.25 | 0.933 | 0.089 | 0.000 | 111.4 | 220.3 |
| keyword:k=5:ctx=2 | 0.917 | 4.25 | 0.933 | 0.100 | 0.467 | 164.6 | 356.4 |
| virgin_nn:k=1:ctx=0 | 0.783 | 4.25 | 0.933 | 0.039 | 0.000 | 6.9 | 8.2 |
| virgin_nn:k=1:ctx=2 | 0.833 | 4.25 | 0.933 | 0.056 | 0.467 | 7.4 | 8.9 |
| virgin_nn:k=5:ctx=0 | 0.967 | 4.25 | 0.933 | 0.106 | 0.000 | 7.1 | 8.2 |
| virgin_nn:k=5:ctx=2 | 0.983 | 4.25 | 0.933 | 0.111 | 0.467 | 7.3 | 8.3 |

## Reading
- Depth k=1->5 (virgin_nn, ctx=0): recall_proxy 0.783->0.967 (delta +0.184), support_rate 0.039->0.106 (delta +0.067).
- Retriever keyword->virgin_nn (k=5, ctx=0): recall_proxy 0.883->0.967 (delta +0.084), support_rate 0.089->0.106 (delta +0.017).
- Context 0->2 (virgin_nn, k=5): support_rate 0.106->0.111 (delta +0.005); context_hit_rate=0.467 (exact/normalized thread-parquet match; misses fall back to the raw query, so the arm mixes context value with query-robustness).
- Groundedness-heuristic columns barely move across arms BY DESIGN: the frozen heuristic scores template shape (DM + 'Check' + length + cite), and every arm retrieves >=1 passage, so it saturates. That is the circularity BASELINE_VS_FINAL.md discloses — the retrieval-sensitive evidence is support_rate, not ground_mean.
- Latency: all arms p50/p95 in low ms (CPU-only, in-process); BM25 over 27k KB docs is the slowest leg.

## What is misleading (mandatory)
- recall_proxy is lexical overlap, not judged relevance: k=5 dominates k=1 mechanically (max over a bigger set). Read it as coverage, not quality.
- support_rate inherits the V3 strict-instrument caveat (JUDGE_AGREEMENT_V3.md): absolute levels are low everywhere; ARM DIFFERENCES are the signal, not absolutes.
- n=60 single-annotator slice: arm deltas have wide CIs; this reframes the +0.005 intent story toward retrieval, it does not replace a judged study.
