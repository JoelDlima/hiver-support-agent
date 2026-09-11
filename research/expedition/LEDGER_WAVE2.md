# LEDGER WAVE-2 — Domains A–M (2026-09-12, ~158 searches; expedition total ~270/300)

Method: 13 domain agents in batches of 3 (system cancels wider fan-out).
SearXNG-first per SXRUNBOOK.md; session-websearch fallback logged per domain.
Wave-1 LEDGER.md stands; below are DELTAS only (confirmations noted once, then deltas).

## SearXNG infrastructure verdict (honest)
- Batches 1–2 (A–F): real multi-engine value (duckduckgo + google-cse + arxiv/openalex/
  crossref hits). Verified 26-result JSON response before sweeps.
- Batches 3–5 (G–M): progressive residential-IP throttling → DDG CAPTCHA,
  google-cse 429/"Suspended", total 0-hit sweeps. Runbook fallback worked as designed.
- Verdict: viable with 6–8s pacing + engine rotation + backoff; NOT a bulk replacement
  for session search from a residential IP. Keep for paced lit-sweeps, dedup script,
  and engine-diversity; do not build automation assuming 100+ q/day keyless.

## Per-domain deltas (ADOPT/CONDITIONAL deltas vs wave-1; REJECTs extend wave-1 list)

A. ML classification — CONFIRMS SetFit/MiniLM head. NEW: LightGBM timeboxed 2nd arm
   (EFB suits sparse TF-IDF; ship iff Δmacro-F1 ≥ +0.01); per-intent ROC/PR thresholds
   (money→precision) + global MSP floor; macro-F1 gate (accuracy hides rare collapse);
   explanations = LogReg coefficients primary + exact LinearSHAP secondary (LIME rejected:
   unstable, foolable); vendored margin+diversity AL loop for 200→500 (BADGE-style,
   no modAL dep); multi-label DEFERRED with 10–15% overlap trigger; rules stay OUTSIDE
   classifier as vetoes.
B. LLMs — ACTION: Groq catalog rotated, qwen2.5 IDs DEAD → re-pin to
   `openai/gpt-oss-20b` + strict:true + Instructor (900 t/s, Apache-2.0, cheapest).
   Prompt-hierarchy obedience 9.6–63.8% ⇒ deterministic fail-closed gate is THE control,
   prompt is decoration (validates current design). Ollama Qwen2.5-7B-Q4 keyless fallback.
   Claim-extraction recipe (Langfuse); verifier 2nd-call on gate-trip only; R1-distills,
   Gemma/Mistral-via-Groq, SSE-on-structured all rejected.
C. RAG — tables confirm no-server at 27k (FAISS-HNSW ~1–3ms vs TF-IDF p50 7ms; deltas
   irrelevant vs 1.4–1.8s LLM gen). NEW cheap win: score-attached citation columns
   (rank/BM25/cosine/RRF/threshold flag) on existing passage UI. Qdrant-local / LanceDB
   (versioning) / Milvus-Lite / FAISS-Flat all CONDITIONAL on triggers. Cohere pricing
   trap documented ($1–2.5/1K + network ~300ms). Citations-can-lie warning: keep gate.
D. Embeddings — MiniLM-L6 default CONFIRMED (Apache-2.0, int8-OV 5.29x). NEW: numpy
   brute-force ~1.5–3ms @27k BEATS FAISS single-query (100% recall, zero dep) → FAISS
   rejected at this scale. Normalize-everywhere discipline (BGE scores live in
   [0.6,1] — rank, don't threshold naively). BGE-small-en-v1.5 CONDITIONAL arm;
   E5-small loses to it; Jina v3+ CC-BY-NC license trap (v2-small Apache but weaker);
   OpenAI embeddings rejected (key/cost/drift). SVD default + Atlas honesty caption
   (2D distances meaningless; neighborhoods are the signal).
E. KB engineering — NEW: BERTweet-parity normalizer (verify parity, keep raw+norm);
   exact-SHA256 dedup + ID map FIRST, MinHash-LSH (0.7–0.8, 5-grams, 128–256 perm)
   second (F1 0.95, 11s vs SimHash 626s); metadata pre-filter; kb_manifest.json
   versioning (NOT DVC); Parquet+ZSTD layer (6.8x smaller, 22–60x queries);
   tweet_id→row→passage→claim provenance; KB quality card per build (5 numbers);
   hash-diff incremental rebuild; thread reconstruction via in_response_to_tweet_id
   (TweetSumm: 49k dialogs; orphan quarantine + 7d gap rule); default_rng+spawn seed
   discipline; ROS-dict over SMOTE on text.
F. Agents-as-builders — scripts win EVEN offline (METR RCT: AI-assist +19% slower
   own-repo; debate gains = ensembling gains; Huang: no intrinsic self-correction).
   ADOPT patterns only: eval-driven tuning discipline (no DSPy dep), single-generator +
   deterministic-gate probe loop. PydanticAI / SmolAgents CONDITIONAL on explicit
   triggers. CrewAI / AutoGen(maintenance mode) / LangGraph-offline / memory-stores
   rejected.
G. Eval tools — Promptfoo CONFIRMED primary (24.7K★, still MIT post-OpenAI; 20–30min
   setup; pass-rate threshold + repeat:3 CI gate). NEW: HHEM-2.1-Open as FREE local NLI
   step for the claim scorer; significance-gated regression (95→92 = noise, gate FLIPS
   not absolutes); pointwise-primary + PRePair-for-A/B-only; golden semver + held-out;
   DeepEval CONDITIONAL (pytest-native); Ragas recipe > dep; LangSmith/OpenAI-Evals
   rejected as primary (copy patterns: annotation queues, prod-trace→dataset).
H. Observability — AMENDMENT to wave-1: emit JSONL via OTel SDK + console/file exporter
   (same zero-ops, standard IDs + gen_ai.* keys + sampling) instead of hand-rolled dicts.
   NEW: structlog (async-safe request IDs); BatchSpanProcessor (~30µs/req); trace↔eval
   join keys (trace_id + eval_run_id); CI-diff quality gate; Jaeger-all-in-one /
   Phoenix-local / Logfire-free all OPT-IN only (SigNoz/LGTM rejected as required:
   1.5–5GB RAM).
I. Backend — NEW specifics: keep `def` handlers (threadpool) + n_jobs=1 + BLAS clamp
   (async+blocking serializes loop; nested parallelism oversubscribes); EventSourceResponse
   + ping=15 + no-buffer headers + is_disconnected cleanup; tenacity (≤3, 429/5xx only)
   + pybreaker (fail_max=5, exclude 429) + shared httpx AsyncClient; RFC-9457 error
   envelope + contract test (3 shapes today = unparseable); pure-ASGI request-ID
   middleware (never read body in middleware); Pydantic-strict per-step gates;
   BackgroundTasks losable-only (eval runs → arq conditional or sync+poll);
   Schemathesis fuzz as dev-dep; slowapi conditional on Redis; WS only for
   client→server mid-stream control.
J. Frontend — NEW specifics: per-panel Suspense + server components (loading.tsx is
   coarse fallback only); fetch+ReadableStream+TextDecoder(stream)+AbortController
   (~40 lines hand-rolled > @microsoft/fetch-event-source stale); rAF batching
   (30–80 → 12–16 renders/s); geometry-matched skeletons (CLS≤0.1) + useTransition on
   refetch; per-panel error/empty/retry + liveness badge (status·request_id·ms/tok-s·retry);
   openapi-typescript (dev-only) + openapi-fetch + zod boundary validation; next-themes;
   motion-lean-or-CSS (full motion 34–60KB unjustified); SWR conditional on polling.
K. Three.js — LEDGER UPHELD WITH DEPTH: ranked-list beats graph views on precision+speed
   (user study) ⇒ list primary, graph secondary; bipartite two-column evidence view
   (force layouts are BLIND to bipartite structure — hairball finding); SVD scatter +
   neighborhood; instancedMesh rules + label caps (≤20); drei barrel risk (989KB via
   one import — lazy-load); canvas a11y parallels mandatory; R3F-v9/React-19 churn
   rejected.
L. Data eng — NEW numbers: Parquet+ZSTD 6.8x + 22–60x queries; Polars 5–8x pandas
   (conditional on profiling; pandas+pyarrow-engine suffices otherwise); DuckDB QA
   sidecar conditional; vectorized str.contains 2x regex (no Snorkel dep at 2.8M);
   manual-strata guards (sklearn stratify raises on singletons); ROS-dict conditional.
M. HITL — NEW buildable spec: Fin-style 3-way router schema {decision, reason_code,
   cited_guideline, confidence}; SQLite `escalations` table + POST /review actions
   (PENDING→APPROVED|EDITED|REJECTED|EXPIRED) + live inbox; risk-tiered
   autonomy_matrix.yaml (intent × tier × confidence → route; model never self-demotes);
   threshold slider showing coverage-vs-risk live; correction-capture →
   golden_candidate.jsonl + promote button (retrain trigger = counter badge, not job);
   5-number analytics strip; hash-chained Attestation audit events; warm-transfer
   payload; SLA chips + keyboard triage conditional; 7-code reason taxonomy.

## Revised-tier inputs (for chat delivery)
Tier-0 fixes unchanged (stale docs, requirements drift, brand-default trap) + NEW: Groq
model re-pin (qwen2.5 IDs dead). Proof tier gains: HHEM free NLI, significance-gated
regression, golden semver, confusion matrix + ranked-list-primary UI. Model tier gains:
LightGBM arm, per-intent thresholds, coefficient explanations, vendored AL loop.
Retrieval gains: score-attached citations (cheapest), numpy-brute-force option, BGE-small
arm. KB tier (new): normalizer parity, MinHash dedup, manifest, Parquet, quality card,
thread reconstruction. Product tier gains: OTel-SDK JSONL, structlog, Suspense panels,
rAF streaming, zod contracts, React-Flow default + bipartite evidence view, review-queue
(HITL) as the flagship new demo surface, autonomy matrix, correction loop.
