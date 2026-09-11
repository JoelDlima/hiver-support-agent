# Performance (§28)

Date: 2026-09-10. Env: Windows, `C:\Hiver\.venv` (measured `sklearn 1.9.0 / pandas 3.0.5`; `requirements.txt` pins 1.7.1/2.2.3 — drift noted, re-pin before release).
Method: `time.perf_counter`, 1 warmup, sequential single-process; percentiles via `np.median/np.percentile` (no p99 — n=20 too small, per research log).

## End-to-end (`agent.handle`: classifier + retriever k=5 + draft + rules)
| Workload | p50 | p95 | mean | min–max | throughput (1 worker, sequential) |
|---|---|---|---|---|---|
| 20 runs (first 20 human-60 texts) | **230.4 ms** | **247.7 ms** | 232.9 ms | 215.2–264.5 ms | **4.3 qps** (4.66 s total) |
| 60-pass (all human-60) | — | — | 234.4 ms | — | 4.3 qps (14.07 s total) |

Per-request breakdown (measured): classifier single `predict` **≈147 ms incl. `joblib.load` per call (dominant)** + retriever-alone p50 **46.0**/p95 **54.2 ms** + template/rules ≈35 ms remainder. Batch-20 classifier call = 0.182 s total (≈9 ms/req amortized) — proving the per-call reload is the bottleneck and the fix (cache pipeline in memory) is worth ≈130 ms/req.

## Index build / load (`data/indexes/index_meta.json` + measured cold load)
| Item | Value |
|---|---|
| n_docs / matrix shape | 106,860 / [106860, 42675] |
| build-machine load (CSV scan) / build (TF-IDF fit + NN fit) / total | 11.9 s / 2.8 s / 17.1 s |
| cold artifact load this machine (`Retriever()` incl. KB lookup) | **2.50 s** |
| classifier load (`joblib`, 11 classes) | **0.15 s** |
| build-time query probe (5 short queries, build machine) | p50 34.6 / p95 38.1 ms (vs 46.0/54.2 on real tweets — longer queries cost more) |

## Model / index file sizes (measured `Get-ChildItem`)
| File | Bytes | MB |
|---|---|---|
| `models/intent_classifier.pkl` | 3,814,280 | 3.64 |
| `data/indexes/tfidf_vectorizer.pkl` | 1,803,909 | 1.72 |
| `data/indexes/nn_index.pkl` | 24,818,320 | 23.67 |
| `data/indexes/tfidf_matrix.npz` | 16,297,998 | 15.54 |
| `data/indexes/doc_ids.csv` | 1,567,658 | 1.50 |
| index total (≈ nn+matrix+vec+ids) | ≈44,487,885 | ≈42.4 |

## Gaps (honest, not measured)
No p99 (sample too small), no concurrent-load test (single-worker qps only), no process RSS measurement (CPU-only; file sizes above, RSS not profiled), no API-server overhead (numbers are in-process `handle()`).
Repro: `$env:PYTHONPATH="C:\Hiver"; C:\Hiver\.venv\Scripts\python.exe C:\Users\Joel\AppData\Local\Temp\opencode\meas_perf.py` (+ `meas_load.py` for load split).
