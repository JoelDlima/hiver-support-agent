# Hiver frontend-next — Next.js + three.js plan

Target: new app `frontend-next/` (separate from `frontend/app.py` Streamlit demo). Backend stays FastAPI at `backend/main.py` (`POST /predict`, `GET /metrics`, `GET /healthz|/readyz`). GROQ key stays server-side (FastAPI env today).

## Chosen stack

- **Next 14 App Router + TypeScript + Tailwind** (route-group shell: `(pages)` dashboard vs `(blank)` auth/standalone). shadcn/ui copy-paste primitives only: Card, Badge, Button, Table, Tabs, Progress, Skeleton, ScrollArea.
- **Data: TanStack Query** for `/metrics` polling (`refetchInterval: 5000`) + `fetch` POST for `/predict`. No global store.
- **3D: three + @react-three/fiber@8** (pairs react@18 on Next 14). Minimal drei (OrbitControls only, direct import). `transpilePackages: ['three']`, Canvas is `'use client'` + `next/dynamic ssr:false`.
- **SSE stream panel:** Next Route Handler `ReadableStream` (`text/event-stream`) proxying FastAPI; client consumes via `EventSource`/fetch-reader hook. Vercel AI SDK `useChat` deferred (FastAPI is source of truth).

## Layout (support dashboard)

- Sidebar (Predict / Retrieval Graph / Metrics / Docs) + header (brand switcher virgin|apple, request ID, latency badge) + main grid:
  1. Query card (textarea, brand select, submit) — POST `/api/predict`.
  2. **Retrieval network graph card (three fiber):** query = center node; top-k `grounding_passage_ids` = satellite nodes sized/colored by `score` (1-distance); edges = single `LineSegments`; click node -> passage text panel. Fallback: 2D ranked list (same data) if WebGL off.
  3. **Confidence bars:** intent confidence + per-passage scores via `Progress` + band caption (auto / review / escalate), not raw % alone.
  4. **Pipeline stage timeline:** validate -> classify -> retrieve -> draft -> escalate, with `draft_path` (template|groq) + `groq_reason` + `decision`/`escalate_reason` per stage; expandable signals packet.
  5. **SSE stream panel:** streams stage events + draft tokens, ends with `[DONE]`; shows `request_id`, `latency_ms`, `truncated` flag.
  6. Metrics card: `predict_count / escalate / auto / avg_latency_ms` + per-brand table, polled.

## Key patterns

- **BFF proxy (never expose keys):** client only calls `/api/predict`, `/api/metrics`. Route Handler reads `process.env.FASTAPI_URL` (+ server-only `GROQ_API_KEY` if Next ever calls Groq directly — default: it doesn't; FastAPI owns it), forwards, strips secrets from errors. No `NEXT_PUBLIC_*` secrets; `server-only` guard; `.env.local` gitignored.
- **SSE proxy:** `export const dynamic = 'force-dynamic'`; `new Response(new ReadableStream(...), {headers: {'Content-Type':'text/event-stream','Cache-Control':'no-cache, no-transform','Connection':'keep-alive'}})`; `data: <json>\n\n` per event + heartbeat; close on complete/error. Keep streams short-lived per predict (serverless timeouts kill infinite SSE; use edge only if persistent).
- **Metrics polling:** `useQuery({queryKey:['metrics'], queryFn: fetch('/api/metrics'), refetchInterval: 5000, staleTime: 4000})`; function form `refetchInterval: ()=> paused? false : 5000`.
- **Fiber graph perf:** `instancedMesh` nodes + one `LineSegments` edges (2 draw calls); memo geometry/material; no `setState` in `useFrame`; `frameloop="demand"` + `invalidate()` on new results; cap visible nodes (top-k=5 default).
- **Honest UX:** show intent + confidence + band + thresholds, passage IDs + scores, draft_path/groq_reason, latency + request ID; empty/error states; never invent times/prices (backend grounding gate already enforces £/HH:MM verbatim).

## What to avoid

- Heavy drei imports (`Environment`, `Stage`, `Cloud`, postprocessing) — bundle bloat, kills first-load.
- Per-passage `<mesh/>` maps, `setState` in render loop, fullscreen-canvas dashboards.
- Client-side keys (`NEXT_PUBLIC_GROQ_API_KEY`), calling Groq/FastAPI directly from browser, leaking key in error bodies/logs.
- Full Vercel AI SDK migration before FastAPI SSE exists; infinite SSE on serverless without edge/timeout plan.
- Pro shadcn blocks/CLI deps; build from primitives + ReUI timeline / shadcn Chart(bar) patterns.

## Next steps (inside C:\Hiver only)

1. `npx create-next-app frontend-next --ts --tailwind --app`; add `three @react-three/fiber @react-three/drei @tanstack/react-query server-only`.
2. Add `app/api/predict/route.ts` + `app/api/metrics/route.ts` proxies -> `FASTAPI_URL` (default `http://127.0.0.1:8000`).
3. Build cards above against live `POST /predict` shape (`intent`, `intent_confidence`, `draft_reply`, `grounding_passage_ids`, `decision`, `signals`, `draft_path`, `groq_reason`, `latency_ms`).
