# 005 — Database / Storage / Serving Decision (Hiver AppleSupport)

Date: 2026-09-10 | Owner: Swarm B | Status: FINAL v1
Base: `docs/research/infrastructure/production.md` + `docs/research/open_source/ecosystem.md` +
DDG verification 2026-09-10 (§7 freshness)

## Context
Serve `classify → retrieve → draft → escalate` statelessly for 100 → 10k users.
Artifacts: TF-IDF vectorizer + classifier (joblib), KB + thread metadata, file indexes.
Constraint: proportional engineering — no K8s/Redis/GPU until `/metrics` evidence.

## Candidates
joblib + CSV/JSONL files + SQLite (WAL, FTS5, read-only prod) | Postgres + pgvector |
Redis/Memcached (cache / rate-limit) | Kafka/Celery/RQ (queue) | K8s | Docker-slim
single image | FastAPI + uvicorn (`--workers N=cores`)

## Evidence (VERIFIED vs ESTIMATE)
- VERIFIED (official, webfetch PyPI 2026-09-10): FastAPI latest = **0.141.1 (Jul 29 2026)**;
  0.115.12 = Mar 23 2025. CORRECTION: `requirements.txt` pins 0.115.12 (17 mo stale)
  while `.venv` already runs **0.141.1** — pin must be bumped; doc text updated here.
  License MIT; requires Python ≥3.10 (covers 3.12).
- VERIFIED (security, websearch PyNest #134 / Starlette GHSA): **CVE-2026-48710 (BadHost)** —
  missing Host-header validation; fix = starlette 1.0.1 (May 21 2026), accepted only by
  fastapi ≥0.133.0 (0.115.x caps starlette<0.47 → blocks the fix, flagged by scanners).
  IMPACT: bumping past 0.133 is a security requirement, not cosmetic. `.venv` 0.141.1
  already compliant — VERIFIED via `pip show fastapi` (0.141.1).
- VERIFIED (official): scikit-learn latest = **1.9.0 (Jun 2 2026)**; 1.8.0 Dec 2025;
  1.7.2 Sep 2025; 1.7.1 Jul 2025. CORRECTION: `requirements.txt` pins 1.7.1 while
  `.venv` runs **1.9.0** — pin must be bumped. `LogisticRegression(multi_class=…)`
  deprecated since 1.5; removal documented as 1.7 but CORRECTED to **1.8**
  (issue #31781 → PR #31795); 1.9.x signature confirms param REMOVED.
  Hiver code safe: `src/classifier.py:48` calls `LogisticRegression(max_iter=1000, C=2.0)`
  with no `multi_class` — VERIFIED by grep. Note: `penalty=` string form deprecated in
  1.8 (use C/l1_ratio) — we don't pass it, no action.
- VERIFIED (sklearn docs): joblib preferred for estimators w/ numpy arrays; load once at
  startup, share read-only (`predict` thread-safe); pin sklearn+numpy/scipy (cross-version
  loads unsupported → `/readyz` version gate); never unpickle untrusted artifacts.
- VERIFIED (SQLite docs): WAL = readers don't block writer (2×+ throughput); limits =
  single-host file, one writer, WAL checkpoint starvation → mitigate with
  `wal_checkpoint(RESTART)` + `busy_timeout=2000ms`; ceiling tens–hundreds rps reads,
  GB-scale DBs — AppleSupport KB (<100k rows, <1 GB) comfortably inside.
- ESTIMATE (production.md §4–5, validate via `scripts/load_smoke.py`): cache-HIT 3–8 ms
  p50; full-pipeline MISS 25–60 ms p50 / 120–250 ms p95 (2 vCPU); ~80–150 rps (2 workers);
  10k users ≈ $25–50/mo self-hosted vs $300–500 (mini-tier) / $3–6k (frontier) LLM API.

## Decision
**FastAPI (bump pin → ≥0.133, `.venv` 0.141.1) + uvicorn workers=cores, stateless;
joblib artifacts loaded once in lifespan; SQLite WAL read-only prod (FTS5 retrieval) +
JSONL fallback; in-memory LRU (1024) + slowapi limits; JSON logs + X-Request-ID +
`/predict /healthz /readyz /metrics`; single `python:3.12-slim` image (~150–250 MB).
Migrate triggers (evidence-gated): Postgres+pgvector iff multi-writer >10/s sustained,
DB >10 GB, or distributed writes; Redis iff multi-replica abuse; GPU/vLLM iff generative
quality proven necessary by eval.**

## Rejected — why
- Postgres/pgvector now: stateful service + backup + ops for a read-only <1 GB KB.
- Redis now: per-worker LRU already captures high-locality repeats ("reset password",
  "warranty"); promote only if hit-rate <15%.
- K8s / Celery / service mesh / Prometheus stack: over-engineering for a single
  CPU-bound container; 1 process/container, scale replicas behind any LB.
- Alpine base: musl wheel pain for sklearn/scipy; `slim` is the sweet spot.
- Gunicorn+UvicornWorker in container: single uvicorn parent managing workers is simpler
  + observable; gunicorn only for bare-VM process management.

## Cost / complexity / failure / scale
- Cost: $6–12/mo (100 users) → $25–50/mo (10k users) — 10–100× cheaper than per-request
  LLM at steady volume (table §5, ESTIMATE with stated assumptions).
- Complexity: `src/app/{main,predict,cache,logging_ctx,limits}.py` + `models/*.joblib` +
  `version.json` + `data/kb.sqlite` (built offline); non-root user, HEALTHCHECK, exec CMD.
- Failure: sklearn drift → pinned image + version gate; SQLITE_BUSY → read-only mount +
  busy_timeout + short reads; per-worker LRU divergence acceptable (monitor hit-rate);
  sensitive intents always escalate regardless of confidence.
- Scale: Stage 0 (1 container) → Stage 1 (compose `--scale api=2–3`, RO file per host) →
  Stage 2 (faiss-cpu/annoy ANN sidecar, mmap) → Stage 3 (Redis/PG/GPU on triggers only).
  Gate before each stage: p95 >300 ms/10 min OR CPU >70% OR hit-rate <15%.
