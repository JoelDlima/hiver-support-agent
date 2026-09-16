# Production / Scalability — AppleSupport Agent (Simple yet Scalable)

**Agent 10 — PRODUCTION/SCALABILITY | Hiver | 2026-09-10**
**Scope:** Stateless FastAPI API for AppleSupport: `classify → retrieve → draft → escalate`. SQLite/joblib index, CPU inference, no over-engineering. No K8s.

## 1. Executive summary / recommendation

Proportional architecture for 100 → 10k users:

```
Client → Uvicorn (1 container, --workers N=cores) → FastAPI app (stateless)
  ├─ POST /predict  (classify + retrieve + draft + escalate, <100ms p50 CPU)
  ├─ GET  /healthz  (liveness: model loaded + sqlite readable)
  ├─ GET  /readyz   (readiness: index + joblib versions match)
  └─ GET  /metrics  (counters, latency histogram, cache hit-rate, JSON)
         │
         ├─ In-memory LRU cache (functools.lru_cache / cachetools, ~1000 entries, per-worker)
         ├─ joblib artifacts loaded once at startup (TF-IDF vectorizer + classifier, read-only)
         └─ SQLite (WAL mode, read-only queries) OR JSONL fallback; FTS5 for retrieval
Logging: stdlib JSON logs + X-Request-ID middleware. Rate limit: in-memory token-bucket/slowapi.
Deploy: single `python:3.12-slim` image (~150–250 MB), `docker compose` optional (api only, no DB container). Scale by adding workers → replicas → ANN index. No Redis, no K8s, no GPU until proven needed.
```

Why this fits: traffic is bursty support Q&A, models are tiny (MBs), inference is CPU-bound milliseconds. Managed LLM API is 10–100x more expensive per request at steady volume and adds latency/variance; self-hosted CPU is near-zero marginal cost.

## 2. Research synthesis (8 queries)

### 2.1 FastAPI stateless scaling (uvicorn workers)
- Production pattern is `uvicorn app:app --workers N` (modern FastAPI docs; `tiangolo/uvicorn-gunicorn-fastapi` image is deprecated — plain uvicorn with `--workers` is enough in a container).
- `N = CPU cores` for async CPU-light workloads (not `(2*cores)+1`, which is for sync WSGI). One container = one concern; scale replicas horizontally behind any LB, keep app stateless so any worker can serve any request.
- Gunicorn+UvicornWorker only justified on a bare VM needing process management; in Docker, single uvicorn parent managing workers is simpler and observable (K8s-style guidance applies to compose too: 1 process per container).
- Must load models in `lifespan` (preload before fork where possible) and keep request handlers async but run sklearn inference in threadpool (`run_in_executor`) if mixed with async I/O to avoid blocking the event loop.

### 2.2 SQLite limits (WAL mode)
- SQLite handles unlimited concurrent readers + one writer well. Default `DELETE` journal mode = DB-level lock, writers block readers. `PRAGMA journal_mode=WAL` = readers don't block writer and vice-versa, mostly sequential I/O, 2x+ throughput.
- Limits for this use case: single-host file only (no NFS multi-host), one writer at a time, WAL file can grow under constant readers (checkpoint starvation) — mitigate with periodic `wal_checkpoint(RESTART)` and `busy_timeout=2000ms`.
- Practical ceiling: tens–hundreds of req/s reads, GB-scale DBs fine. AppleSupport KB (<100k rows, <1 GB) is comfortably inside SQLite. Migrate to Postgres/pgvector only if: multi-writer >10 writes/s sustained, DB >10 GB, or need distributed writes.
- Operational rules: `WAL + synchronous=NORMAL + busy_timeout + immutable KB file mounted read-only in prod`, short transactions, pre-build FTS5 index offline.

### 2.3 joblib model serving
- sklearn official guidance: `joblib.dump/load` for estimators with numpy arrays (more efficient than pickle). Load once at startup, share read-only across requests (thread-safe for `predict`).
- Pin `scikit-learn==x.y.z + numpy/scipy` in image; models trained on one version are unsupported on another (`InconsistentVersionWarning`). Freeze via Docker. Store alongside: train snapshot ref, source commit, lib versions, CV score.
- Never unpickle untrusted artifacts (arbitrary code exec). Only load from `models/` baked into image or signed volume. Consider `skops.io` later for untrusted sharing — out of scope now.
- Pattern: `vectorizer.joblib + classifier.joblib + kb.sqlite + version.json` loaded in lifespan; `/readyz` fails if versions mismatch.

### 2.4 Caching (in-memory LRU)
- `functools.lru_cache(maxsize=1024)` / `cachetools.TTLCache` is thread-safe, ~20–40ns overhead, ideal for repeated support questions (high locality: "reset password", "warranty", "refund" repeat).
- Caveats: args must be hashable (normalize text → lower/strip → tuple/str key), per-process cache (each uvicorn worker has its own — acceptable; hit-rate still high), never cache with side effects. Expose `cache_info()` via `/metrics`.
- Expected win: cache hit cuts ~50–150ms → ~5ms (dict lookup + template render). Size 500–2000 entries ≈ few MB. No Redis needed until multi-replica hit-rate proven too low.

### 2.5 Rate limiting
- `slowapi` (Starlette/FastAPI port of flask-limiter) or `fastlimiter` token-bucket: `@limiter.limit("60/minute")` per IP, in-memory backend, 429 with `Retry-After`. Zero infra.
- For this agent: `POST /predict: 30–60/min per IP + 500/min global burst`; `/metrics`, `/healthz` excluded or looser. Window-based (fixed/sliding) is 3–4x faster than token-bucket in benchmarks — either is fine at this scale; pick slowapi fixed-window for simplicity.
- Distributed (Redis) only when >1 replica and abuse observed. Until then, per-replica limits are proportional.

### 2.6 Structured logging + request IDs
- Standard: `structlog` or stdlib `logging` JSON formatter + `asgi-correlation-id` / `fastapi-request-context` middleware: read `X-Request-ID` or generate UUID, echo in response header, bind to all logs in request scope (`contextvars`).
- Log per request: `request_id, method, path, status, duration_ms, classifier_label+conf, retrieval_top1_score, escalated(bool), cache_hit(bool)`. JSON to stdout (Docker collects); pretty console only in dev.
- `/metrics` exposes counters (no ELK/Prometheus server needed initially): `requests_total, escalations_total, latency_p50/p95 (in-process histogram), cache_hits_total, model_version`. Scrapeable later by Prometheus if needed — keep format simple JSON + optional `# HELP` text.

### 2.7 Cost per request: tiny self-hosted CPU vs LLM API
- LLM API 2026 refs: `GPT-4o $2.50/$10.00 per 1M in/out`, `GPT-4o-mini $0.15/$0.60`, `Claude Sonnet ~$3/$15`, embeddings `$0.02/1M` (small). Self-hosted CPU: $6–12/mo single VPS (2 vCPU/2–4 GB) or ~$25/mo managed container.
- AppleSupport request without LLM: TF-IDF+LogReg + SQLite FTS + template ≈ $0.000001–0.00001 marginal (amortized compute only). Same request via frontier LLM (800 in + 200 out tokens): ~$0.002–0.004 (GPT-4o) or ~$0.0002–0.0004 (mini). At 10k users × 5 req/day = 1.5M req/mo, LLM = $300–$6,000/mo vs CPU box = $12–$50/mo.
- Break-even for GPU self-hosted LLM is ~300–500M output tokens/mo or ~1.2B total tokens/mo — irrelevant here because we don't need a generative LLM per request. Rule: use small classifier + retrieval + templates; call LLM API only for optional `draft-polish` on escalated/complex cases (<5% traffic) or not at all in v1.

### 2.8 Docker minimal
- Best practice: `python:3.12-slim` (~95 MB base), multi-stage or single-stage with layer caching (`requirements.txt` before code), non-root user, `HEALTHCHECK`, exec-form `CMD`, `.dockerignore`. Result ~145–250 MB vs ~1.1 GB for full `python:3.12`.
- Avoid Alpine for sklearn/scipy (musl wheel pain, slower builds); `slim` is the sweet spot. `uvicorn[standard]` (uvloop+httptools) for speed. Official FastAPI Docker docs pattern applies directly.

## 3. Proposed architecture (proportional, no over-engineering)

### 3.1 Components
| Component | Choice | Why |
|---|---|---|
| API | FastAPI, stateless, Python 3.12 | automatic validation/docs, async, tiny |
| Server | `uvicorn app.main:app --workers $CORES` | no gunicorn in container |
| Classify | `vectorizer.joblib + clf.joblib` (TF-IDF + LogReg/LinearSVC, calibrated) | <10 MB, CPU ms, versioned |
| Retrieve | `kb.sqlite` FTS5 (`articles(id,title,body,url,updated)`) top-3, or `kb.jsonl` fallback | zero service, file-backed |
| Draft | deterministic template per intent + retrieved snippet + citations | no LLM needed, safe |
| Escalate | rule: `conf < 0.55 OR top1_bm25 < threshold OR intent==sensitive → escalate=true + reason` | measurable, auditable |
| Cache | `lru_cache(maxsize=1024)` on normalized query → full response (minus request_id) | biggest latency win |
| Store | SQLite WAL read-only in prod; writes only offline rebuild | concurrency-safe |
| Observability | JSON logs + X-Request-ID + `/metrics` + `/healthz` + `/readyz` | no external stack |
| Deploy | 1 Docker image, optional compose | portable, cheap |

### 3.2 Request flow (`POST /predict`)
```
1. middleware: assign/echo X-Request-ID, start timer, rate-limit check
2. validate PredictRequest {query: str(1..2000), locale?, top_k=3, debug=false}
3. normalize query → LRU lookup → HIT? return cached (with new request_id) : MISS
4. classify: X=vectorizer.transform([q]) → label, conf, top3 probs        (~5–15ms)
5. retrieve: FTS5 MATCH + bm25 ranking, filter by predicted intent        (~5–20ms)
6. draft: fill intent template with top1 snippet + url                    (<1ms)
7. escalate decision + reason_codes                                        (<1ms)
8. log JSON line + update in-memory metrics, store LRU entry
9. return PredictResponse {label, confidence, articles[], draft, escalated, escalate_reason, request_id, model_version, latency_ms}
```

Pydantic sketch:
```python
class PredictRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=5)
    locale: str = "en"

class Article(BaseModel):
    id: str; title: str; url: str | None; score: float

class PredictResponse(BaseModel):
    label: str; confidence: float
    articles: list[Article]
    draft: str
    escalated: bool; escalate_reason: str | None
    request_id: str; model_version: str; latency_ms: float; cache_hit: bool
```

Endpoints: `POST /predict` (rate-limited), `GET /healthz`, `GET /readyz`, `GET /metrics`. No auth in v1 beyond rate limit; add API key header only when exposed publicly.

### 3.3 Project layout (minimal)
```

  deployment\Dockerfile.simple
  deployment\docker-compose.simple.yml   # optional, api-only (see §7)
  research\infrastructure\production.md  # this file
  src\app\main.py        # FastAPI app, lifespan loads joblib+sqlite
  src\app\predict.py     # classify+retrieve+draft+escalate pipeline
  src\app\cache.py       # LRU wrapper + normalize()
  src\app\logging_ctx.py # request-id middleware + JSON formatter
  src\app\limits.py      # slowapi limiter config
  models\*.joblib + version.json
  data\kb.sqlite         # built offline, shipped read-only
```

### 3.4 What we explicitly DON'T build (anti-goals)
No Kubernetes, no Redis/Memcached, no Postgres, no Celery/RQ, no vector DB service, no GPU, no per-request LLM call, no service mesh, no Prometheus/Grafana stack in v1. Each has a defined trigger in §6.

## 4. Latency estimate (CPU, single replica, 2 vCPU)

Assumptions: `MiniLM` embeddings NOT in hot path (TF-IDF only); FTS5 indexed; `top_k=3`; warm process.

| Path | p50 | p95 | Notes |
|---|---|---|---|
| Cache HIT (`/predict`) | 3–8 ms | 10–20 ms | dict lookup + JSON ser |
| Cache MISS, full pipeline | 25–60 ms | 120–250 ms | classify 5–15 + FTS 5–20 + overhead; p95 = cold page cache / GC / concurrent burst |
| `/healthz`, `/readyz`, `/metrics` | 1–3 ms | 5–10 ms | no model work |
| Throughput (2 workers, 2 vCPU) | ~80–150 rps sustained | — | beyond this add workers/replicas, not code changes |

How to verify: `scripts/load_smoke.py` (50 concurrent × 1000 reqs, report p50/p95 + cache hit-rate); log `latency_ms` histogram in `/metrics`. If p95 >300ms sustained, first check SQLite `PRAGMA` + checkpoint, then add worker, then ANN.

## 5. Cost estimate (self-hosted CPU vs LLM API)

Assumptions: 5 req/user/day × 30d; avg LLM-equivalent 800 in + 200 out tokens (only for comparison — v1 uses $0-marginal template path); cache hit-rate 30% at scale.

| Users | req/mo | Self-hosted CPU (this design) | LLM API (mini-tier, e.g. 4o-mini) | LLM API (frontier, e.g. GPT-4o/Sonnet) |
|---|---|---|---|---|
| 100 | 15k | $6–12/mo (1× shared 1–2 vCPU) → **~$0.0005/req** | ~$3–5/mo → ~$0.0002/req | ~$30–60/mo |
| 1,000 | 150k | $12–25/mo (1× 2 vCPU) → **~$0.0001/req** | ~$30–50/mo | ~$300–600/mo |
| 10,000 | 1.5M | $25–50/mo (1–2× 2–4 vCPU) → **~$0.00003/req** | ~$300–500/mo | ~$3,000–6,000/mo |

Takeaway: at 10k users this design is **10–100x cheaper** than per-request LLM, with lower p95 latency and no token-variance risk. Optional LLM polish on <5% escalated traffic adds <$25/mo even at 10k users — acceptable if quality data demands it.

## 6. Scaling path (workers → replicas → ANN)

1. **Stage 0 (now, 0–1k users):** 1 container, `workers=cores`, SQLite WAL read-only, LRU 1024, slowapi memory limits. Done.
2. **Stage 1 (1k–10k users / >100 rps):** `docker compose up --scale api=2–3` behind Caddy/Nginx or cloud LB; SQLite file replicated read-only per host (rebuild offline, redeploy). No code change (stateless).
3. **Stage 2 (KB >100k docs or FTS p95 >50ms):** add ANN sidecar index (`faiss-cpu` IVF or `annoy`, `embeddings.npy` precomputed, mmap): FTS → ANN re-rank, still CPU, still file-backed. ~10–30ms top-k at 1M vectors on CPU.
4. **Stage 3 (triggers only):** Redis for shared rate-limit/cache if multi-replica abuse; Postgres+pgvector if multi-writer or >10 GB; GPU/vLLM only if generative quality proven necessary by eval. Each migration gated on `/metrics` evidence, not speculation.

Load test gate before each stage: p95 >300ms for 10 min OR CPU >70% sustained OR cache hit <15%.

## 7. Deploy (Docker minimal + optional compose)

Built artifact: `deployment/Dockerfile.simple` (see file). Key decisions: `python:3.12-slim`, venv, non-root `appuser`, `HEALTHCHECK /healthz`, exec CMD with `${WORKERS:-2}`.

```dockerfile
# summarized — see deployment/Dockerfile.simple for runnable file
FROM python:3.12-slim
# ... install reqs, copy src+models+kb, non-root, healthcheck
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-2} --no-access-log"]
```

Optional `deployment/docker-compose.simple.yml` (create only when needed — single service, no DB):
```yaml
services:
  api:
    build: { context: .., dockerfile: deployment/Dockerfile.simple }
    ports: ["8000:8000"]
    environment: { WORKERS: "2", LOG_JSON: "1", KB_PATH: "/data/kb.sqlite" }
    volumes: ["../data/kb.sqlite:/data/kb.sqlite:ro"]
    read_only: true
    restart: unless-stopped
```

Run: `docker build -f deployment/Dockerfile.simple -t hiver-applesupport:simple . && docker run -p 8000:8000 hiver-applesupport:simple`.

## 8. Observability & ops (minimal but sufficient)

- **Logs:** JSON to stdout: `ts, level, request_id, path, status, duration_ms, label, conf, top1_score, escalated, cache_hit, model_version`. `LOG_JSON=1` in prod, pretty in dev.
- **Metrics (`GET /metrics`):** `uptime_s, requests_total, cache_hits_total{hit_rate}, escalations_total{by_reason}, latency_ms{p50,p95}, model_version, kb_docs, kb_mtime`. Enough for alerts without Prometheus.
- **Health:** `/healthz` = process alive; `/readyz` = joblib+sqlite loaded and version check passes (container orchestrator / compose `healthcheck` uses `/healthz`).
- **Rate limit:** 429 JSON `{detail, retry_after_s}`; log `rate_limited=true`.
- **Ops:** rebuild KB offline (`scripts/build_kb.py → kb.sqlite`), bump `version.json`, redeploy image. Rollback = previous image tag. Backup = versioned `kb.sqlite` + `*.joblib` files.

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| sklearn version drift breaks joblib | pin versions, bake models into image, `/readyz` version gate |
| WAL growth / SQLITE_BUSY under burst | read-only mount in prod, `busy_timeout`, short reads, offline checkpoint |
| Per-worker LRU divergence | acceptable; monitor `hit_rate` in `/metrics`, promote to shared cache only if <15% |
| Prompt-injection / sensitive intents over-answered | escalate list (payments, safety, account-takeover) always escalates regardless of confidence |
| Scope creep into K8s/LLM-everything | this doc is the gate: no new infra without `/metrics` evidence + eval delta |

## 10. Next steps (for builder agents)

1. Scaffold `src/app/main.py` per §3 (+ lifespan, middleware, `/predict`, `/metrics`, `/healthz`, `/readyz`).
2. Add `scripts/build_kb.py` (CSV → `kb.sqlite` FTS5) and `scripts/train_classifier.py` (→ `models/*.joblib` + `version.json`).
3. Wire `Dockerfile.simple` build + smoke test (`/predict` p50/p95 script).
4. Record eval (accuracy, escalation precision/recall) before any LLM or ANN addition.

---
*Sources: FastAPI server-workers + Docker deployment docs; SQLite WAL/concurrency docs; sklearn model-persistence docs; functools.lru_cache docs; slowapi/fastlimiter repos; structlog/correlation-ID middleware patterns; OpenAI/API pricing + self-host break-even analyses 2025–2026; Docker Python/FastAPI best-practice guides. Full URLs in research log entry 2026-09-10 (Agent 10).*
