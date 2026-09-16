# Next.js + Groq Starters for Hiver Revamp — Borrow List (patterns only)

**Date:** 2026-09-11 | **Scope:** `.` only | **Current:** FastAPI `backend/main.py` (`/predict` brand-aware) + `src/groq_draft.py` (keyless fail-closed) + Streamlit `frontend/app.py` (direct `src.agent` import) → revamp to Next.js frontend, keep FastAPI backend.
**Constraint:** Never copy large code verbatim — patterns only, cite sources. Licenses verified from README excerpts Sep 2026; re-check `LICENSE` before vendoring.

## Method (15 attempts, 11 OK, 4× 429 retried OK)

| # | Query | Status | Key source |
|---|---|---|---|
| 1 | best Next.js + FastAPI starter 2025-2026 | 429 → retried as #6 OK | — |
| 2 | reddit r/nextjs Next.js FastAPI starter | OK | r/nextjs 2026-01-04 server-components+FastAPI guide (u/Ok_Animator_1770); r/nextjs self-host thread; r/FastAPI Dec-2025 LLM template; nemanjam fork |
| 3 | reddit r/reactjs shadcn dashboard | OK | r/reactjs threads (suniljoshi19, Then_Abbreviations77, al-amin_Rifat); shadcndashboard repo |
| 4 | reddit r/LocalLLaMA support-agent demo UI | 429 → retried as #13 OK | — |
| 5 | reddit r/MachineLearning judge/eval dashboard | OK | r/MachineLearning JudgeGPT thread; LLM-as-judge agent-eval thread; evalstack; llm-regression-detector |
| 6 | Next.js FastAPI starter open source 2025 (fast) | OK | fastapi/full-stack-fastapi-template; vintasoftware/nextjs-fastapi-template; nemanjam fork; Vercel starter |
| 7 | react-three-fiber knowledge-graph RAG viz (fast) | OK | r3f-rag-viz; graphrag-workbench; Cognitive-Cartographer; graphite |
| 8 | support-agent demo UI open source (fast) | OK | openai-support-agent-demo; openai-cs-agents-demo; jawwad-ali agent; anthropic-krzim demo |
| 9 | SSE streaming chat Next.js FastAPI | 429 → retried as #11 OK | — |
| 10 | shadcn dashboard template | 429 → retried as #12 OK | — |
| 11 | FastAPI StreamingResponse SSE chat (fast) | OK | FastAPI SSE docs (`EventSourceResponse`); theneuralbase/stackpractices/mljourney/dev.to patterns |
| 12 | shadcn admin dashboard Next.js (fast) | OK | Kiranism/next-shadcn-dashboard-starter; shadcndashboard/next-shadcn-dashboard |
| 13 | reddit r/LocalLLaMA RAG chatbot UI (fast) | OK | r/LocalLLaMA threads (NakedxCrusader, ReserveOdd1984, Proof-Exercise2695, SemperPistos, anedisi, JealousZebra1) |
| 14 | LLM eval dashboard promptfoo/langfuse (fast) | OK | langfuse/langfuse; promptfoo/promptfoo; NeekChaw/llm-judge; numoru agent-evals-template |
| 15 | Next.js Groq streaming starter (fast) | OK | vercel-labs/ai-sdk-starter-groq; groq/groq-frontend-base; xeven777/next-groq; groq-aisdk-chatbot |

Reddit coverage: r/nextjs + r/reactjs + r/LocalLLaMA + r/MachineLearning (4/4 required subs).

---

## 1. Next.js + FastAPI starters

### 1a. `fastapi/full-stack-fastapi-template` — 45,219★ / MIT
- Repo: https://github.com/fastapi/full-stack-fastapi-template
- **Borrow:** OpenAPI-generated typed frontend client pattern; Docker-Compose local-services shape (as doc reference only); Playwright e2e + pytest split; Traefik/HTTPS reverse-proxy note for self-host. Cite: repo README (FastAPI + SQLModel + Pydantic + PostgreSQL + React/Vite + shadcn/ui + generated client + pytest + Actions).
- **NOT copy:** React+Vite+Chakra frontend (Hiver revamp is Next.js + shadcn); Postgres/SQLModel/auth stack (Hiver is file-index TF-IDF NN, no DB server, <15min CPU repro); FastAPI Cloud / Traefik deploy (overkill for demo).

### 1b. `vintasoftware/nextjs-fastapi-template` — 324★ / MIT
- Repo: https://github.com/vintasoftware/nextjs-fastapi-template (push 2025-12-17, v0.0.8)
- **Borrow:** End-to-end type-safety pattern (FastAPI+Pydantic ↔ TypeScript+Zod via OpenAPI, `openapi-fetch` typed client); `uv` + Docker Compose + pre-commit shape; Vercel-deployable async backend note. Cite: repo highlights (Zod+TS, shadcn/ui, openapi-fetch, uv, Docker, Vercel).
- **NOT copy:** `fastapi-users` JWT auth + dashboard auth flow (Hiver has no login; adds attack surface); fully-async DB query layer (Hiver `/predict` is sync CPU-bound — FastAPI runs `def` in threadpool per ecosystem.md §4).

### 1c. `nemanjam/full-stack-fastapi-template-nextjs` — 18★ / MIT
- Repo: https://github.com/nemanjam/full-stack-fastapi-template-nextjs + writeup https://nemanjamitic.com/projects/2025-12-31-full-stack-fastapi-template-nextjs/ + r/nextjs threads (u/Ok_Animator_1770 2026-01-04; r/PythonProjects2 2025-11-26)
- **Borrow:** The single most relevant pattern for Hiver: Next.js-16 Server Components + Server Actions proxying FastAPI (HttpOnly cookie auth enables SSR); Hey-API `client-next` generated client; Suspense/error-boundary per-route; runtime-only env (`next-public-env` style) for reusable Docker builds; `main` (Docker) vs `vercel-deploy` (two Vercel projects + Neon) branch split. Cite: repo checklist + author writeup (proxied requests, no Traefik/Nginx needed, Zod-validated env).
- **NOT copy:** Auth/cookie machinery itself (Hiver needs no auth — copy the *proxy-through-Next* shape, not the login pages); Turborepo monorepo + GitHub-login + Sentry/emails roadmap (bloat for Hiver repro); Vercel two-project wiring until Hiver actually deploys.

### 1d. Vercel `nextjs-fastapi-starter` (digitros/nextjs-fastapi lineage)
- Template: https://vercel.com/templates/fast-api/next-js-fastapi-starter
- **Borrow:** Minimal monorepo routing convention (`/api/*` → Next.js route, `/svc/api/*` → FastAPI service via `vercel.json` services); local-dev port split (3000/8000) with rewrite. Cite: Vercel template docs + r/nextjs self-host thread (nothing serverless-specific about the frameworks — self-hostable on one server).
- **NOT copy:** Python serverless-function hosting assumption (Hiver serves `uvicorn backend.main:app` single-process; keep local `next.config.js` rewrite to `127.0.0.1:8000`, not Vercel functions).

## 2. react-three-fiber RAG / knowledge-graph viz

### 2a. `lz1834career/r3f-rag-viz` — 2★ / MIT
- Repo: https://github.com/lz1834career/r3f-rag-viz — demo https://r3f-rag-viz-demo.vercel.app — npm `r3f-rag-viz-core` + `r3f-rag-viz-react`
- **Borrow:** `buildGraphFromRetrieval(chunks, edges)` → `RAGGraph {nodes, edges}` adapter (maps relevance score → node size/color); `onSceneChange` event back to app (node-move/select); view-state export (hide/annotate/export JSON/PNG, undo/redo). Peers: `three`, `@react-three/fiber`, `@react-three/drei`, `zustand`. Cite: repo README + topics (r3f, d3, knowledge-graph, rag, nextjs).
- **NOT copy:** Full monorepo/npm publish setup (Hiver needs one small component, not two packages); 500+ node path (repo roadmap says LOD/instancing not done — cap Hiver graph at top-k=5 passages, 2D fallback first).

### 2b. `lyon-industries/graphrag-workbench` — license MIT per README (stars: verify live, low)
- Repo: https://github.com/lyon-industries/graphrag-workbench
- **Borrow:** Next.js-16 + R3F + `d3-force-3d` + SSE-progress + persisted-logs operator shape; full-screen graph + search + community-isolation + Inspector (entity + strongest connections). Cite: repo highlights (Microsoft GraphRAG 3.1.0 via `uv`, LanceDB/parquet local, cancellable server).
- **NOT copy:** Microsoft GraphRAG indexing pipeline + LanceDB + local/cloud model presets (Hiver retrieval is TF-IDF NN file-index, p50 ~7ms — no GraphRAG build step); desktop-style project manager (Hiver needs one read-only viz tab, not a workbench).

### 2c. `gdhpsk/Cognitive-Cartographer` (R3F + d3-force-3d + Zustand v5 + shadcn)
- Repo: https://github.com/gdhpsk/Cognitive-Cartographer (backend on `backend` branch)
- **Borrow:** Scene-component split (`scene.tsx` ForceGraph + CameraController + tooltips; `file-upload.tsx`; shadcn `ui/`); click-node → slide-out detail panel; search-highlight; camera-animate-to-selection; `GET /graph → {nodes, edges}` minimal contract. Cite: repo stack table (Next.js-16 App Router, R3F/drei, d3-force-3d, Zustand v5, Tailwind v4).
- **NOT copy:** WebSocket PDF-upload + attention-head heatmap + WebGL2 GLSL + Motion/GSAP/Aceternity effects (heavy, Hiver-inappropriate); `WSS /ws/*` session protocol (Hiver uses plain GET/POST + optional SSE stream).

### 2d. `pradhankukiran/graphite` — MIT per README (Next.js-15 + Django + Neo4j)
- Repo: https://github.com/pradhankukiran/graphite
- **Borrow:** Hybrid-retrieval framing (vector similarity + graph traversal) as *doc reference* for future upgrade note; `react-force-graph-2d/3d` as lighter alternative to hand-rolled R3F; multi-LLM connector list incl. Groq/Cerebras/OpenRouter. Cite: repo stack (Next.js-15, Zustand, Radix, Django-Ninja, Neo4j-5, Celery).
- **NOT copy:** Entire backend (Django + Postgres-16 + Neo4j-5 + Redis-7 + Celery workers + Daphne) — violates Hiver CPU-only/file-index/<15min constraints; auto entity-extraction pipeline (Hiver passages are historical replies, not KG triples).

## 3. Support-agent demo UI

### 3a. `openai/openai-support-agent-demo` — MIT
- Repo: https://github.com/openai/openai-support-agent-demo
- **Borrow:** Dual-view chat shape (customer view + agent view); suggested-response (streaming) with edit-before-send; Relevant-articles panel wired to knowledge base; suggested-actions with auto-execute only for non-sensitive tools. Cite: repo README (multi-turn, file-search tool, vector-store upload, KB display, function-calling, streaming suggestions).
- **NOT copy:** OpenAI Responses-API + file-search/vector-store backend (Hiver retrieval is local TF-IDF; no vendor store); `cancel_order`/`reset_password` live tool calls (Hiver has no action tools by design — injection safety comes from having nothing to hijack); demo order IDs (ORD1001) — use Virgin Delay-Repay/amendment flows instead.

### 3b. `openai/openai-cs-agents-demo` — MIT (verify LICENSE live)
- Repo: https://github.com/openai/openai-cs-agents-demo
- **Borrow:** Triage → specialist router (flight/booking/seat/FAQ/refund) as *UI visualization* reference (show intent + route + guardrail in Hiver debug expander); ChatKit chat-interface quality bar. Cite: repo README (Python Agents-SDK backend + Next.js UI + orchestration visualization).
- **NOT copy:** Agents-SDK multi-agent orchestration (Hiver decision: deterministic pipeline validate→classify→retrieve→draft→escalate→validate, no agent framework per `docs/research/agents/orchestration.md`); airline tool set (not rail).

### 3c. `jawwad-ali/ai-customer-support-agent` — license: verify live (repo does not state in excerpt)
- Repo: https://github.com/jawwad-ali/ai-customer-support-agent (Next.js-16 + FastAPI + pgvector + Redis, 258 tests, Docker/K8s)
- **Borrow:** FastAPI-as-thin-layer + async-job-ID + frontend-polling (return 202 + `GET /jobs/{id}`; Redis-down fallback to sync); semantic-search threshold + top-3 + escalate-on-no-match; sentiment-gated escalation (refund/legal/angry/no-match); per-channel tone truncation. Cite: repo README (tool table `search_knowledge_base`/`escalate_to_human`, endpoint table, thin-layer rationale).
- **NOT copy:** Postgres+pgvector + Redis + OpenAI-embeddings + Gmail/WhatsApp webhooks (Hiver: TF-IDF file-index, no external services); K8s manifests (no K8s per ecosystem.md); outbound Gmail/Twilio wiring (explicitly unfinished upstream — do not inherit half-built delivery).

### 3d. Others scanned (no borrow without verification)
- `anthropic-krzim/claude-code-mcp-demo` (Next.js + TF-IDF search + mood + shadcn): borrow only the context-inspector idea (click grounding-status → full RAG context); do not copy Claude-only + MCP GitHub wiring.
- `10xshivam/Cenra` (35★ MIT, Next.js-16 widget + dashboard + LangGraph + Qdrant): borrow embeddable-widget `/embed` page idea; do not copy Node/Express + LangGraph + Qdrant + Neon/Prisma stack.
- r/LocalLLaMA consensus (threads 2025-02 → 2026-03): OpenWebUI / LibreChat / AnythingLLM / Dify / R2R / Flowise dominate self-host RAG-UI recommendations; AnythingLLM repeatedly under-answers on long PDFs; NotebookLM good but not deployable; chatbot UIs that force OpenAI-style request shapes annoy custom-RAG owners. Cite: r/LocalLLaMA threads (NakedxCrusader 2026-03-11; ReserveOdd1984 2025-08-19; Proof-Exercise2695 2025-12-12; SemperPistos 2025-09-05; anedisi 2025-11-11; JealousZebra1 2025-02-10). Implication for Hiver: build a thin bespoke Next.js chat panel over Hiver's own `/predict` schema rather than adopting an OpenAI-shaped UI.

## 4. SSE streaming chat (Next.js + FastAPI)

- Docs: https://fastapi.tiangolo.com/tutorial/server-sent-events/ — `EventSourceResponse` + `ServerSentEvent(data/event/id/retry)`; POST-SSE supported (needed for chat bodies); `raw_data="[DONE]"` sentinel for pre-formatted terminators.
- Guides: theneuralbase (AsyncOpenAI + `stream=True` + `StreamingResponse(text/event-stream)`); stackpractices (async generator + `data: {json}\n\n` + `done` event + fetch-reader with buffer split on `\n\n`); mljourney (Anthropic `messages.stream` + `X-Accel-Buffering: no` + `get_final_message` usage); dev.to/ayinedjimi (GeneratorExit handling + curl `--no-buffer` test + `@microsoft/fetch-event-source` for POST).
- **Borrow for Hiver:** `POST /predict/stream` returning `StreamingResponse` with `media_type="text/event-stream"`, headers `Cache-Control: no-cache` + `X-Accel-Buffering: no`; event framing `token` (JSON `{text}`) → `done` (`{reason, usage}`) → `error` (`{message}`); client fetch-reader (EventSource is GET-only, unusable for chat POST); Groq path uses OpenAI-compatible client with `stream=True` against `https://api.groq.com/openai/v1`, temp 0, finish_reason check before parse; fail-closed: any stream error → emit `error` event and fall back to template draft (same `draft_path/groq_reason` contract as `src/groq_draft.py`).
- **NOT copy:** Sync `OpenAI()` client inside `async def` (blocks event loop — use `AsyncOpenAI`); bare-text frames without JSON envelope (breaks on newlines; breaks token/done/error discrimination); Nginx without `X-Accel-Buffering: no` (buffers kill realtime); retrying 400/401 or streaming bulk eval traffic (Hiver policy: one attempt on request path, jittered backoff offline-only; never bulk Groq in eval gates).

## 5. Judge / eval dashboards

### 5a. `promptfoo/promptfoo` — ~22k★ / MIT (verify LICENSE live)
- Repo: https://github.com/promptfoo/promptfoo — guide `site/docs/guides/llm-as-a-judge.md`
- **Borrow:** Layered assertion pattern (L1 deterministic `is-json`/`contains`/regex exactness → L2 `llm-rubric`/`g-eval`/`factuality`/`select-best` for open-ended quality); multi-judge voting + injection-safe judge prompts; `promptfooconfig.yaml` + `npx promptfoo view` + CI action (block merge on regression). Cite: llm-as-judge guide (candidate output + rubric + judge model → `{pass, score, reason}`).
- **NOT copy:** Full red-team/vuln-scan + cloud-trace + Langfuse-managed-prompts surface (Hiver judge is heuristic offline + pinned `gpt-4o-mini` hook behind wκ≥0.60 + safety-recall≥0.90 gate per `evaluation/virgin/JUDGE_AGREEMENT.md` — keep promptfoo as CI comparator, not the judge of record).

### 5b. `langfuse/langfuse` — OSS self-hostable (YC W23; license: verify — MIT/Apache family)
- Repo: https://github.com/langfuse/langfuse
- **Borrow:** Trace → dataset → eval loop (OpenTelemetry/LangChain/OpenAI-SDK/Vercel-AI-SDK integrations; boolean/categorical judge-score types per PR #12836); playground jump-from-bad-trace. Cite: repo README (evals + observability + prompt management + datasets) + PR #12836 (boolean `BOOLEAN` score persistence).
- **NOT copy:** ClickHouse + Postgres self-host stack (Hiver eval store is CSVs + SQLite; no server DB at 107k docs); vendor-cloud dependency for gates (gates must run keyless/offline).

### 5c. `satyamshivam13/LLM_Judge_Evaluation` — license: verify live (FastAPI + SQLAlchemy + Streamlit)
- Repo: https://github.com/satyamshivam13/LLM_Judge_Evaluation
- **Borrow:** Bias-mitigations to mirror in Hiver judge docs: pairwise position-swap (run twice, tie-on-flip, lowered confidence on disagree); verbosity-flag (longer-won + wide margin); self-family warning; YAML rubrics with per-score anchors; cost/latency-per-call tracking. Cite: repo README (MT-Bench/G-Eval/Prometheus lineage, 4 modes pointwise/pairwise/reference/batch).
- **NOT copy:** Dual-provider OpenAI+Anthropic hard dep + Docker-Compose service (Hiver keyless default); batch mode without backoff (upstream roadmap gap — Hiver keeps paced/offline judge calls).

### 5d. `anejakartik/evalstack` — OSS (verify LICENSE live; FastAPI + SQLite → Next.js dashboard)
- Repo: https://github.com/anejakartik/evalstack
- **Borrow:** Run-list → run-diff (judge means + deltas, 10-bucket histograms, top regressions/improvements, per-prompt matched table, event-level word-LCS diff); `@evalstack.trace` decorator + `evalstack run <eval.yaml>` CLI + Fly.io/Vercel deploy split. Cite: repo README (SDK captures calls, FastAPI judges, SQLite store, Next.js+Tailwind browser).
- **NOT copy:** Braintrust-priced positioning + Postgres-next + Slack-alert roadmap (copy the *diff views*, not the SaaS surface).

### 5e. Others scanned
- `Dakshjain1604/LLM-response-Judge` (React+Vite+FastAPI, multi-provider incl. Ollama, rubric editor, critical-bottom-10%): borrow CSV/JSON golden-import + weighted-rubric editor + client-side-only keys; do not copy server-stored keys or auto-rewrite score predictions.
- `archminor/llm-as-a-judge` (2026-04-02): borrow blinded pairwise + `judge_repeats: 3` + `majority_vote` aggregation + 3-layer (format/content/expression) separation with Layer-1 score-cap; do not copy vendor-matrix complexity.
- `numoru-ia/agent-evals-template` (Promptfoo + DeepEval + Langfuse + Go guard): borrow merge-blocking regression-guard (threshold `--threshold 0.05`, Faithfulness ≥0.85) as CI reference; do not copy Go/LiteLLM/Go-agent stack.
- r/MachineLearning: JudgeGPT thread (rubric behavioral anchors per score level reduce leniency clustering; configurable judge model + prompt from UI; default `qwen2.5:7b`) and agent-eval thread (single-criterion + anchors + strict format + bias warnings; rules-first + G-Eval/DAG-metric decomposition). Cite: r/MachineLearning threads (JudgeGPT; Cristhian-AI-Math 2025-10-01).

## 6. shadcn dashboard templates

### 6a. `Kiranism/next-shadcn-dashboard-starter` — 6,000+★ (6,700+ per about page) / MIT
- Repo: https://github.com/Kiranism/next-shadcn-dashboard-starter — demo https://shadcn-dashboard.kiranism.dev/
- **Borrow:** Feature-based folder layout; dashboard shell (sidebar + header + content + infobar); analytics cards + Recharts graphs with parallel routes and per-panel loading/error states; TanStack Table (search/filter/sort/pagination + React-Query prefetch + cache invalidation) for golden/judge tables; TanStack Form + Zod; nuqs URL-state; kbar command palette; 6+ themes via switcher; `AGENTS.md`/`CLAUDE.md` agent-pattern file. Cite: repo README (Next.js-16, React-19, Tailwind-v4, shadcn on Base UI, Clerk, TanStack, Zod, nuqs, Zustand).
- **NOT copy:** Clerk auth + Organizations + Billing/RBAC + Sentry (Hiver demo has no users/billing — strip to unauthenticated dashboard); Evil Charts/Dice-Table extras until needed.

### 6b. `shadcndashboard/next-shadcn-dashboard` — MIT with attribution footer
- Repo: https://github.com/shadcndashboard/next-shadcn-dashboard — docs https://shadcndashboard.dev/docs
- **Borrow:** Tickets-app page as the model for Hiver escalations queue (Blog/Notes/Tickets apps out of the box); auth-page set + form layouts + data-table + profile/activity as copy-shape reference; `next-themes` dark-mode toggle. Cite: repo README (Next.js App Router, shadcn + Base UI, Tailwind-v4, Recharts, TipTap).
- **NOT copy:** Attribution-footer requirement propagates if vendored — keep dependency as inspiration, not vendored theme, or retain footer link; TipTap blog editor (unused by Hiver).

### 6c. r/reactjs pointers
- `Tailwind-Admin/free-tailwind-admin-dashboard-template` (via u/suniljoshi19 2025-12-19 / 2026-04-18; u/al-amin_Rifat 2025-09-11): borrow auth-pages + charts + tables + i18n + light/dark shape; verify license live before reuse. `marmelab/shadcn-admin-kit` (via reactjs thread): borrow auth-preconfigured kit reference only. `silicondeck/shadcn-dashboard-landing-template` (2025-09-23): Vite+React only — not for Next.js revamp, ignore except component styling cues.

## 7. Next.js + Groq chat starters (directly on Hiver's drafter path)

### 7a. `vercel-labs/ai-sdk-starter-groq` — license: verify live (Vercel template terms)
- Repo: https://github.com/vercel-labs/ai-sdk-starter-groq — template https://vercel.com/templates/next.js/vercel-x-groq-chatbot
- **Borrow:** AI-SDK streaming chat (`useChat` + tool-integration weather-example shape + reasoning-model support) with Groq via Marketplace key injection; shadcn/ui + Tailwind chat shell on Next.js App Router. Cite: template features (streaming, multi-provider swap in lines, tools, reasoning).
- **NOT copy:** Vercel-Marketplace key wiring + Vercel-KV/auth-secret env (Hiver: `GROQ_API_KEY` env-only, OpenAI-compatible `base_url=https://api.groq.com/openai/v1`, fail-closed to template per `src/groq_draft.py`); default-model choice (Hiver pin migrates off sunset `llama-3.3-70b-versatile` 2026-08-16 → `gpt-oss-20b/120b` or `qwen3.6-27b` per gap top-up finding).

### 7b. `groq/groq-frontend-base` — MIT
- Repo: https://github.com/groq/groq-frontend-base
- **Borrow:** Minimal Groq frontend split: server-side chat-completion route (`src/app/api/`) + client hook (`use-completion.ts` / `use-completion-tools.ts`) + `chat-component.tsx`; Biome lint/format. Cite: repo README (Next.js-TS + Tailwind + shadcn + server + client hook).
- **NOT copy:** Committed `.env.local` shape (Hiver: never commit keys; `gsk_...` placeholder + `gsk_test_fake` sentinel only); demo prompts/tools (replace with Virgin rail grounding: ≤280ch, £/HH:MM verbatim-match gate).

### 7c. Others
- `xeleven777/next-groq` (Vercel AI SDK + model dropdown + timing + dark mode): borrow response-time display → Hiver latency metric; do not copy pages-router + app-router mix.
- `groq/groq-aisdk-chatbot` (AI-SDK + shadcn + Tailwind): borrow RSC/Suspense/Server-Action chat shape; default `gpt-3.5-turbo` is stale — use Hiver's Groq pin.

---

## Recommended borrow list for Hiver revamp (ordered)

1. **Shell:** Kiranism starter layout + Tickets-app (shadcndashboard) → Hiver pages: Chat / Golden-200 / Judge-agreement / Failures / Costs. Strip Clerk/Billing/Sentry.
2. **API bridge:** nemanjam Server-Actions-proxy-FastAPI + Vercel `/svc/api` routing → Next.js proxies to `uvicorn backend.main:app`; keep sync `def /predict` (threadpool) + add `POST /predict/stream` (SSE).
3. **Chat:** `groq-frontend-base` hook+route split + `ai-sdk-starter-groq` streaming → Groq-behind-gate with `draft_path/groq_reason` + confidence captions (<0.45 auto-escalate; money <0.70 review) from current `frontend/app.py`.
4. **RAG viz (phase 2, capped):** `r3f-rag-viz` `buildGraphFromRetrieval` + Inspector + export-JSON/PNG over top-k=5 passages; 2D fallback default, 3D opt-in.
5. **Eval:** promptfoo layered asserts in CI + evalstack run-diff views + LLM_Judge_Evaluation swap/verbosity guards → extend `evaluation/virgin/` (keep heuristic judge + κ/swap/verbosity gates; LLM hook pinned, advisory until wκ≥0.60 + safety-recall≥0.90).
6. **Streaming protocol:** FastAPI `EventSourceResponse`/`StreamingResponse` + `token/done/error` JSON envelope + `X-Accel-Buffering: no` + `AsyncOpenAI` + `[DONE]` sentinel.

## Explicitly NOT copying (Hiver constraints)

- No Postgres/Neo4j/Redis/Qdrant/LanceDB/ClickHouse server, no K8s, no Docker-first, no GPU/torch-train/vLLM, no managed vector DB (ecosystem.md §3 + technology-decisions 001/005).
- No auth/billing/organizations/Sentry/Clerk (demo is unauthenticated; keeps repro <15min CPU).
- No live tool calls / refunds / email-send tools (injection safety by absence; escalate-with-packet instead).
- No ungrounded amounts/times in templates (DR30 bands + booking-ref ask only; £/HH:MM verbatim gate stays).
- No API keys in code/client (env-only `GROQ_API_KEY`; client-side key storage seen in LLM-Judge demos is rejected).
- No large verbatim copies — reimplement patterns above against Hiver's `/predict` schema + brand configs in `src/brands.py`.
