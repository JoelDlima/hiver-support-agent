# Decision Matrix — Hiver AppleSupport (Swarm B, 2026-09-10)

> Number policy (§13): VERIFIED = measured or official-doc sourced. Everything else is
> labeled **ESTIMATE** (relative, must be validated on TWCS/AppleSupport slice).
> No invented absolute accuracy numbers.

| Component | Option | Quality | Speed | Cost | Scalability | Maturity | Complexity | Decision |
|---|---|---|---|---|---|---|---|---|
| Intent classifier | TF-IDF 1–2g + LogReg C=2 (baseline) | Good baseline: 76–81% acc ESTIMATE (tweet analogues) | Train <1 min, infer <5 ms CPU ESTIMATE | $0 VERIFIED | Single host; workers=cores | sklearn 1.9.0 VERIFIED (latest Jun 2026); BSD | Low (Pipeline+joblib) | **ADOPT (mandatory baseline)** |
| Intent classifier | MiniLM-L6-v2 22M + linear head (primary) | Best trade ESTIMATE; GIST variant if underfit | ~5–15 ms CPU / <5 ms GPU ESTIMATE | $0 | Same | Apache-2.0 VERIFIED; stable | Low-Med (torch CPU opt) | **ADOPT (primary T1)** |
| Intent classifier | DistilBERT 66M fine-tune | +small on formal text ESTIMATE; needs tweet fine-tune | ~20–50 ms CPU ESTIMATE | $0 | Same | Apache-2.0 VERIFIED | Medium | Ablation only |
| Intent classifier | DeBERTa-v3-small | Highest MNLI 88.3 VERIFIED but heavy embed | Slower than DistilBERT ESTIMATE | $0 | Same | MIT VERIFIED | Medium | Accuracy-ceiling ablation |
| Intent classifier | Keyword rules | 1.0 weak / 0.517 human-60 VERIFIED (circular) | Fastest | $0 | Trivial | N/A | Lowest | Weak-label boot + guardrail only |
| Retrieval | TF-IDF/BM25 + sklearn NN files | Strong on templated replies VERIFIED (p50 35 ms) | p50 34.6 / p95 38.1 ms VERIFIED; 17 s build VERIFIED | $0 VERIFIED | To ~1M docs, then ANN | sklearn/V ERIFIED stable | Low | **ADOPT (baseline now)** |
| Retrieval | + MiniLM dense + RRF + rerank | +1–3 pts top-k ESTIMATE; +30–40% w/ rerank ESTIMATE | +rerank ~50 ms/100 pairs CPU ESTIMATE | $0 | Same + ANN trigger | Apache-2.0/MIT VERIFIED | Medium | **ADOPT (Phase-2 ticket)** |
| Retrieval | FAISS-cpu file index | Same quality at 107k (no gain) | ms (unneeded headroom) | $0 license | To billions w/ IVF/HNSW/GPU | v1.15.0 Jul 2026 VERIFIED; MIT | Medium | Defer (>1M docs or p95>200 ms) |
| Retrieval | Chroma embedded | Prototype-grade | Good ESTIMATE | $0 license + ops | Limited | Active but CVE backlog VERIFIED | Medium | Reject (serving) |
| Retrieval | LanceDB embedded | Same as file index at our scale | Good ESTIMATE | $0 license + ops | Edge/file story | Active VERIFIED | Medium | Reject |
| Retrieval | pgvector | Good to ~50M if PG present VERIFIED (guides) | 1M vec ~8 ms ESTIMATE | Infra + ops | To ~50M VERIFIED | Active (0.8/0.9) VERIFIED | High (stateful svc) | Reject (no PG in stack) |
| Retrieval | Elasticsearch 9.4.6 | Best hybrid-in-one-engine | Good | Infra + ops | High | 9.4.6 Sep 2026 VERIFIED | High | Reject |
| Retrieval | Pinecone/Qdrant-cloud | Same quality, network hop | +latency/variance | Recurring $ | High | Mature | High (keys/egress) | Reject (cost) |
| Draft | Per-intent templates + citations | Ground 4.75/5, ≥4 rate 1.0 VERIFIED (local) | <1 ms | $0 | Trivial | N/A | Lowest | **ADOPT (v1 default)** |
| Draft | gpt-4o-mini json_schema/strict | High ESTIMATE; 8–12% complex-schema drift ESTIMATE | 0.8–1.2 s e2e ESTIMATE | $0.15/$0.60 per 1M VERIFIED; ~$0.0002–0.0005/req ESTIMATE | Stateless; Batch −50% | GA 2024-08-06 VERIFIED; snapshot 2024-07-18 | Low (1 call + retry) | **ADOPT (gated Phase-2)** |
| Draft | claude-haiku-4-5 | Better tone ESTIMATE | TTFT ~500–900 ms ESTIMATE | $1/$5 per 1M VERIFIED (4–8× mini) | Same | GA Jan 2026 VERIFIED | Low | Eval ceiling only |
| Draft | Llama-3.1-8B / Mistral-7B / Gemma-2 self-host | App-enforced struct only | 0.5–3 s CPU-quant ESTIMATE | Infra + ops | GPU for SLA | Custom-gated (Llama/Gemma) VERIFIED; Mistral-7B Apache-2.0 VERIFIED | High | Offline contingency only |
| Orchestration | Plain Python + Pydantic + sklearn | ≥95% shape-correctness by construction | p95 = ms + ≤1 LLM call | $0 marginal | Branches as ifs | Pydantic v2 / sklearn 1.9 VERIFIED | Lowest | **ADOPT** |
| Orchestration | LangGraph / LlamaIndex WF / PydanticAI / Agents SDK / CrewAI / MAF / ADK | No measured gain on fixed pipeline | N×LLM + tools (unbounded) | 10–50× ESTIMATE | Overkill features | All stable 2025–26 VERIFIED (001–004) | High | Reject (DSPy offline-opt revisit) |
| Store/Serve | FastAPI + uvicorn + joblib + SQLite-WAL + LRU | Sufficient (gates in 005) | HIT 3–8 ms / MISS 25–60 ms p50 ESTIMATE; 80–150 rps ESTIMATE | $25–50/mo @10k users ESTIMATE | workers→replicas→ANN | FastAPI 0.141.1 Jul 2026 VERIFIED; CVE-2026-48710 needs ≥0.133 VERIFIED | Low | **ADOPT (bump pin ≥0.133)** |
| Store/Serve | Postgres+pgvector / Redis / K8s / GPU | Same quality at our scale | Same or +hops | 10–100× infra ESTIMATE | Needed past triggers only | Mature | High | Reject until triggers fire |
| Eval | Deterministic + heuristic + golden-200 | Required coverage (4 layers) | $0 + 2–3 d labeling (one-off) | ~$0 | Every release | sklearn κ/RAGAS VERIFIED | Medium | **ADOPT (now)** |
| Eval | LLM-judge gated (κ bars) | Licensed iff w-κ≥0.60 + safety-FAIL R≥0.90 | Batch −50% | Low $ | Regression runs | Biases documented VERIFIED | Medium | **ADOPT (gated)** |
| Eval | BLEU/ROUGE/BERTScore as proof | Misleading (r≈0.22–0.32 VERIFIED) | Cheap | $0 | N/A | Mature but wrong tool | Low | Diagnostic-only; banned as launch evidence |

Version corrections applied (Sep 2026 verification): sklearn pin 1.7.1→1.9.0 (multi_class removed in 1.8, not 1.7);
FastAPI pin 0.115.12→≥0.133 (0.141.1 latest; CVE-2026-48710); FAISS 1.12.0→1.15.0 latest (decision unchanged);
gpt-4o-mini $0.15/$0.60 confirmed current.
