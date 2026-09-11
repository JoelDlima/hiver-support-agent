# Cost (§29)

Date: 2026-09-10. All cloud/price figures are **ESTIMATES** (labeled) — no measured cloud bill exists. Local compute marginal cost is measured ($0 — laptop CPU, builds in seconds).

## Assumptions (ESTIMATES, stated so the table can be re-cut)
- Traffic: 10 req/user/month → 100 / 1k / 10k users = **1k / 10k / 100k req/month** (support traffic is sparse; peak << measured 4.3 qps single-worker, so one 2vCPU host covers all three tiers).
- Host class: always-on **2vCPU** small host, budget VPS (≈$6/mo) → managed PaaS (≈$50/mo) **ESTIMATE** band. (Reference, verified 2026-09-02: Azure Container Apps Consumption list prices ≈$0.0864/vCPU-hr active, free grant 180k vCPU-s + 2M req/mo — our volumes fit inside/near the grant with scale-to-zero; the $6–50 band is the always-on 2vCPU equivalent, NOT a measured Azure bill.)
- LLM comparator (task spec, ESTIMATE): gpt-4o-mini class **$0.0002–0.0005/req**.

## Monthly cost (ESTIMATE)
| Users (req/mo) | Local stack: host (EST.) | Local: per-req CPU | LLM-API alternative (EST.) | Note |
|---|---|---|---|---|
| 100 (1k) | $6–50 | $0 | $0.20–0.50 | LLM ≈ noise; host dominates both |
| 1k (10k) | $6–50 | $0 | $2–5 | local flat, LLM linear |
| 10k (100k) | $6–50 | $0 | $20–50 | ≈100k LLM reqs ≈ one managed host/mo |

## One-time / fixed (measured, $0 marginal)
- Ingest + embedding: TF-IDF fit + NN build **17.1 s total** (`index_meta.json`: load 11.9 + build 2.8) on laptop-class CPU — one-time, re-runnable; **no embedding-API spend** (local TF-IDF, no MiniLM calls in final path).
- Retrieval per request: local cosine NN ≈46 ms (p50) — **$0/req**.
- Index artifacts ≈42 MB on disk; classifier 3.6 MB — negligible storage.

## Reading
- Local-stack cost is **flat** across tiers (single 2vCPU handles 100k req/mo at 4.3 qps with headroom); LLM cost is **linear** — breakeven vs hosting appears around the 10k-user tier at the top of the spec band.
- Final path uses **zero LLM calls** (template draft + rules), so the LLM column is a foregone alternative, not a current spend. Adding an LLM draft head later would move per-req cost from $0 into the $0.0002–0.0005 band — gate on measured quality delta (model routing §18).
