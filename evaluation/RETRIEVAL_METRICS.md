# Retrieval metrics — TF-IDF NearestNeighbors (§17)

Date: 2026-09-10. Corpus: 106,860 outbound AppleSupport replies (`data/indexes`, shape [106860, 42675]).
Index: `TfidfVectorizer(sublinear_tf, 1–2-gram, min_df=2, max_features=50000, stop_words=english)` + `NearestNeighbors(n=5, cosine, brute)`.

## Method
- Proxy definition (task-spec): hit = top-k contains ≥1 passage with `score = 1 − cosine_dist > 0.08` (same 0.08 as `decide_escalation.no_grounding`). This measures **availability/coverage, not relevance** — there are no judged relevant passages per query.
- Queries: all 60 `golden_human_60.csv` inbound texts, `retriever.query(t, k=5)`, 1 warmup, `time.perf_counter`, sequential, venv (`sklearn 1.9.0` measured; `requirements.txt` pins 1.7.1 — env drift noted).
- Repro: `$env:PYTHONPATH="C:\Hiver"; C:\Hiver\.venv\Scripts\python.exe C:\Users\Joel\AppData\Local\Temp\opencode\meas_retrieval.py`

## Results (measured 2026-09-10, this machine)
| Metric | Value |
|---|---|
| recall@1 proxy (score>0.08) | **1.000 (60/60)** |
| recall@3 proxy (score>0.08) | **1.000 (60/60)** |
| recall@5 proxy (score>0.08) | **1.000 (60/60)** |
| top-1 score mean | 0.365 |
| top-1 score p50 / p10 / min | 0.352 / 0.260 / 0.222 |
| retriever-alone latency p50 | **46.0 ms** (n=60, k=5) |
| retriever-alone latency p95 | **54.2 ms** (mean 46.6, min 39.0, max 59.4) |
| build-time probe (index_meta.json) | p50 34.6 ms / p95 38.1 ms (5 short probes, build machine — shorter queries, hence faster) |

## Interpretation
- Coverage is **saturated**: min top-1 score (0.222) is 2.8× the 0.08 gate, so `no_grounding` never fires from score on this set — in `final` it only fires via empty/exception path (retriever=None ablation: unresolvable 0.833 → 0.133 with retrieval). The 0.08 threshold is a **safety net, not a discriminator**.
- Do NOT report recall@k proxy as relevance: per Agent-1 research log, high recall@k coexists with wrong answers (Facet-RAG Evidence Override). Answer-level groundedness (§22 heuristic) is reported alongside, never instead.
- Latency context: sklearn brute-NN is the correct baseline at 106k docs (benchmark cross-check: SKLNN strong for small/medium; FAISS scales better, ES fastest raw — see research log 2026-09-10 Swarm C). Upgrade criterion: move to FAISS/HNSW only if retriever p95 breaches budget at production concurrency.
- Follow-up (honest gap): recalibrate threshold (e.g. 0.25 near p10) or run a judged recall@k on sampled query–passage pairs; current proxy cannot distinguish good from bad retrieval.
