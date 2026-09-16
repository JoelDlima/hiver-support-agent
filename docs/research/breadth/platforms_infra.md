# Breadth: support platforms + infra for Hiver

Date: 2026-09-11. Context: VirginTrains niche, FastAPI + SQLite/joblib file indexes (27,172 Virgin docs, p50 ~7ms), Docker (`deployment/Dockerfile.simple`). 20 websearch queries, full DATE/QUERY/SOURCE/FINDING/RELEVANCE/IMPACT ledger in `docs/research_log.md` (2026-09-11 Breadth: platforms + infra entry). All writes inside `.` only.

## 1. Comparison table (one line per query)

| # | Topic | Signal (Sep-2026) | Hiver fit |
|---|---|---|---|
| 1 | Intercom Fin | Avg 76% resolution (8k+ customers, top 80-93%, +1%/mo); $0.99/outcome; Fin AI Engine; Automation=Involvement x Resolution; assumed vs confirmed resolution | Benchmark honesty model; outcome-pricing comparator |
| 2 | Zendesk AI | Claims 80% but 20-40% typical / 60-80% optimized (UrbanStems 39%, Lush 60%); ~$1.50 committed / $2.00 PAYG + $55-169/agent + $50 Copilot; dual-model verification May-2026 | Same benchmark; self-report audit warning |
| 3 | Decagon | AOPs (NL -> structured logic) + multi-model mesh + memory + guardrails + trace + A/B + Watchtower; Cloud Run/Tasks/Gemini; <400ms voice; 80%+ deflection | Pattern reference only; no tools layer adopted |
| 4 | Sierra | Constellation 15+ task-routed models + supervisors + auto-failover; Agent OS composable tasks; ADP memory; Ghostwriter builder | Validates task-split; no 15-model ops |
| 5 | Delay Repay claims data | ORR 2.5M closed P1-4 2025 (+5%); DR15 25% / DR30 50%/100%/return; 28-day window; Table 4410 CSV; Core Data periodic | Bands + window + CSV source; never quote amounts |
| 6 | Darwin timetable API | LDB JSON + Push Port + Timetable files via Rail Data Marketplace (OGL); XML free, SOAP free to 5M/4wk; HSP 1-yr; NRDP -> RDM late-2026; Evolution Aug-2026 | Sanctioned live source; LDB-first integration |
| 7 | TransportAPI fares | Managed REST/WebSocket/GTFS (Rail Info + Rail Performance delay-repay archive + Bus Fares); freemium; ORR 2026 fares frozen (regulated -0.1% vs RPI +4.1%) | Fare/archive candidate if fare failures top |
| 8 | Lost property | MissingX (LNER/LNR/SWR/ScotRail/TPE/TfW/Avanti, from/to -> TOC, no hold) vs NotLost (AI photo + auto-match + courier) vs Nova Find; no central DB | Route to TOC form/office; ask journey+description |
| 9 | WhatsApp (Twilio/Meta) | $0.005/msg + Meta template (~$0.0034 util/auth); 24h window free-form; Oct-1-2026 service replies billable; 4 categories + tiers; pre-approval | Channel cost model; budget the Oct change |
| 10 | Conversations/SMS | $0.05/MAU (200 free) + $0.0083/SMS seg + carrier + $0.25/GB media; 1000 parts/50 non-chat, 1600 chars, 30 APS | One-conversation multi-channel shape |
| 11 | SendGrid triage | MX -> mx.sendgrid.net, POST multipart, 2xx else 3-day retry, spam score, raw MIME; parse -> categorize -> handler | Email intake without mailbox code |
| 12 | Stripe refunds | POST /v1/refunds (partial, multi <= original); succeeded/requires_action/failed/cancelled; Idempotency-Key 255ch/24h | NO refund tool; idempotency pattern only |
| 13 | Notion KB | Workers hosted runtime (credits Aug-2026), External Agents API, replace (<10k) vs delta syncs, Markdown API, MCP -91% tok | KB-sync pattern; stay local-file |
| 14 | Confluence KB | REST -> Markdown -> version-checked sync -> hybrid RRF -> /search; Airflow selective-load by version | Adopt version-check, not the stack |
| 15 | Docker FastAPI+Next | FastAPI exec CMD + proxy-headers; Next standalone ~110MB vs ~1GB; compose dev/prod + watch; Caddy/Nginx + Alembic prod | U1 recipe |
| 16 | Caddy vs Nginx SSE | Caddy 3-line auto-HTTPS vs Nginx 25-line+certbot; +22% 1KB Caddy / +16% 1MB Nginx; SSE: buffering off + no-cache + timeouts + ping | U1 picks Caddy default |
| 17 | Litestream | WAL-stream to S3, no code change, 14k* Apache-2.0; config prod vs CLI dev; PITR, snapshots, 24h retention | U2 core |
| 18 | pgvector managed | Neon $0.106/CU-h + $0.35/GB vs Supabase $25+ ($0.125/GB, PITR $100/7d); HNSW settled (m16-32, ef 64-200, build-after-load) | Deferred per Decision 001 |
| 19 | Upstash rate limit | FixedWindow/SlidingWindow SDK, prefix+id, deny-list, multi-limit; free 500k/mo, $0.20/100k, $10/250MB; budget-cap; +1-5ms HTTP | U3 core (multi-worker) |
| 20 | Turnstile | Free 20 widgets/10 hostnames, Ent unlimited/200/custom; no DNS needed; invisible PoW; vs reCAPTCHA Ent 10k free then $8/90k; Bot Mgmt separate | U3 bot gate |

Sources: intercom.com/fin, fin.ai, Zendesk docs/blog, decagon.ai, sierra.ai, ORR dataportal Table 4410, nationalrail.co.uk developers, transportapi.com, missingx.com/notlost.com, Twilio docs/pricing, SendGrid parse docs, Stripe API refs, Notion dev docs, GitHub confluence-rag/gateway, FastAPI/Docker docs, Caddy/Nginx benches, litestream.io, Neon/Supabase pricing, Upstash docs, Cloudflare Turnstile product/pricing. Full per-query SOURCE in research log.

## 2. Top-3 upgrades Hiver should adopt

### U1 — Prod compose: Caddy + FastAPI + Next standalone, SSE-safe (effort: S)
- What: `compose.prod.yml` with three services (caddy:2.11, api from `deployment/Dockerfile.simple` + `--proxy-headers`, web from Next `output:standalone` ~110MB). Caddyfile: `site { reverse_proxy api:8000, web:3000 }` (auto-HTTPS + renewal, no certbot). SSE route: `header_up X-Accel-Buffering no`, `Cache-Control: no-cache`, 15s keep-alive ping, terminal `[DONE]`, client honors `Retry-After`.
- Why: single-VM Hiver scale does not need K8s; Caddy kills the #1 outage class (expired cert) with 3 lines vs 25; standalone cuts image ~1GB -> ~110MB; SSE checklist (rows 15-16) already matches `stream_groq_draft` shape.
- Fail-closed: proxy error -> 502 + template path unaffected (draft degrades, never blocks triage); no secret in Caddy logs.
- Verify: `docker compose -f compose.prod.yml up --build -d`, curl `/predict` + `/predict/stream` through Caddy (assert chunks arrive unbuffered, `[DONE]` terminal), cert renew dry-run.

### U2 — Keep SQLite/file indexes + add Litestream S3 streaming (effort: S, defer Postgres)
- What: run `litestream replicate` sidecar (config file, not CLI) over the SQLite/file-index volume to S3-compatible store; nightly `replicate -once -enforce-retention` snapshot; documented `restore -o` runbook + quarterly restore drill (`PRAGMA integrity_check`).
- Why: Hiver at 27k docs / p50 7ms has zero Postgres need (Decision 001 reaffirmed by row 18: small Neon ~$15 vs Supabase ~$30, HNSW build cost unjustified); Litestream adds DR + point-in-time with no code changes and ~$0 storage at Hiver sizes.
- Fail-closed: replica lag/failure never blocks serving (async WAL ship); restore goes to scratch path first, swap only after integrity check.
- Verify: kill -9 api + volume wipe on staging, `litestream restore`, assert KB/index row counts + golden repro identical; revisit Postgres only on trigger: multi-writer, >1M vectors, or JOIN-heavy workload.
- Explicitly not adopted now: pgvector/Neon/Supabase, FAISS/ANN, hosted embeddings (rows 18 + prior breadth).

### U3 — Abuse + channel intake: Upstash sliding-window + Turnstile + SendGrid Parse (effort: S/M, no refund tool)
- What: (a) rate limit `/predict` by IP/API-key: `SlidingWindow(60 req / 60s)` via Upstash if multi-worker else in-process slowapi (same semantics); 429 JSON + `Retry-After`; budget-cap so bill cannot exceed ceiling. (b) Turnstile invisible widget on public demo `/predict` form (server `siteverify`), fail-open locally / fail-closed publicly (challenge-fail -> escalate-with-packet, never serve ungrounded draft to bots). (c) Optional email intake: SendGrid Inbound Parse MX -> POST -> Hiver `handle(text)` -> draft-or-escalate reply; WhatsApp via Twilio Conversations only for outbound escalation notices with pre-approved utility template (inside 24h window, Oct-2026 billable math budgeted).
- Why: rate limit stops API abuse across workers (row 19, +1-5ms acceptable off hot зазем); Turnstile stops bot-farmed eval/demo gaming without CAPTCHA UX (row 20, free 20 widgets); Parse reuses the deterministic pipeline for email with zero mailbox code (row 11); Stripe row stays a negative lesson: money actions keep human approval + Idempotency-Key if ever built.
- Fail-closed: limiter error -> allow single-process fallback (log) but Turnstile-fail + PII-dense -> DM-redirect/escalate template; never auto-refund, never send £/HH:MM not in passages.
- Verify: k6 200-rps burst (429s with correct header, p95 unaffected for allowed), bot replay blocked by Turnstile mock-fail, Parse fixture email -> correct intent + draft_path logged; WhatsApp cost sheet ($0.005 + Meta template) attached before any send enabled.

## 3. Explicitly NOT adopted (with trigger)
- Provider/model switch for support answers (Fin/Zendesk/Decagon/Sierra are benchmarks, not deps): revisit only if Hiver judge-gated quality drops and failure analysis names the drafter.
- Live Darwin/TransportAPI wiring: read-only lookup trial only if timetable/fare failures top the failure suite (F2-class); otherwise keep no-guess + redirect (compliant per ORR licence duty).
- WhatsApp/SMS send + Stripe refunds as agent tools: never autonomous (Air Canada liability); human-approved, idempotent, capped if ever added.
- Notion/Confluence as serving KB: file KB + version-checked sync stays; sync to Notion/Confluence only as publishing mirror.
- Nginx Plus / K8s / managed Postgres now: Caddy + compose + Litestream covers single-VM prod; revisit at multi-host or 1M+ vectors.
