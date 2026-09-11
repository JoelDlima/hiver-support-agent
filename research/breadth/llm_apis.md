# Breadth: LLM APIs + inference services for Hiver

Date: 2026-09-11. Context: support triage (VirginTrains primary), Groq `qwen/qwen3.8-27b` live drafter, fail-closed templates (`src/groq_draft.py`). 20 websearch queries, full DATE/QUERY/SOURCE/FINDING/RELEVANCE/IMPACT ledger in `research/research_log.md` (2026-09-11 Breadth entry). All writes inside `C:\Hiver` only.

## 1. Provider comparison (speed / price / structured output)

| Provider | Speed signal (same-prompt live bench, Llama-3.3-70B) | Price signals (Sep-2026, per 1M in/out) | Structured output | Hiver fit |
|---|---|---|---|---|
| Groq (current) | ~400 tok/s, TTFT ~180ms; llama-3.3-70b ~280-394 tok/s docs/bench | gpt-oss-120b $0.15/$0.60 (cached $0.075); llama-3.3-70b $0.59/$0.79; Qwen3.6-27B $0.60/$3.00; free 30 RPM | strict:true on gpt-oss-20b/120b + qwen3.8-27b (constrained decoding); strict:false best-effort; NO stream/tools with SO | KEEP. qwen-primary + gpt-oss-fallback + template ladder is correct |
| Cerebras | ~1200 tok/s (3x Groq), TTFT ~100ms; 8B 1800 tok/s / 70B 450 tok/s (16-bit) | gpt-oss-120b $0.35/$0.75; 1M free tok/day | strict:true supported (schema subset); OpenAI-compat | Fallback candidate ONLY if Groq preview discontinued. No switch now |
| Together | GPU-class (~H100 band, task-dependent) | gpt-oss-120b-class from ~$0.15/$0.60 band; broad open catalog | json_schema via response_format (Pydantic/Zod helpers) | Alternative fallback, no advantage for Hiver's 2-model ladder |
| Fireworks | ~90 tok/s (slowest of four on same bench) | gpt-oss-120b $0.15/$0.60; DeepSeek-V4-Flash $0.14/$0.28; 1M-ctx options | json_schema + grammar mode; native OpenAI strict shape (LiteLLM downgrade bug fixed Jun-2026) | No switch; widest ctx options irrelevant at Hiver prompt sizes |

Sources: ashstep2/inference-benchmark; Cerebras blog; UsagePricing + Tickerr Sep-2026; console.groq.com structured-outputs; Fireworks/Cerebras/Together docs; litellm#29604; developers.openai.com.

## 2. Per-topic findings (one line each)

| # | Topic | Finding | Relevance to Hiver |
|---|---|---|---|
| 1 | Speed | TTFT close race (100-250ms); throughput 3-13x gap compounds on agents, not single drafts | Groq ~1s/draft is fine; no move |
| 2 | Price | gpt-oss-120b ~= $0.13/1k drafts; qwen-27B-class ~6x more on output | Cost ladder validated; cap off gpt-oss leg |
| 3 | Structured output (providers) | strict:true now on qwen3.8-27b; stream+SO still 400s everywhere | Pin strict:true non-stream; keep two-path design |
| 4 | Structured output (OpenAI) | Guarantee comes from required+closed schema, not flag alone | Hiver schema already compliant; check refusal/finish_reason |
| 5 | Streaming SSE | EventSourceResponse+yield, 15s ping, no-cache, no-buffer, [DONE] | `stream_groq_draft` already conformant |
| 6 | Prompt caching (Groq) | Auto, 50% off, skips rate limits; gpt-oss legs ONLY, qwen gets none | Byte-identical static prefix for fallback hits |
| 7 | Prompt caching (OpenAI/Anthropic) | Input-only discount (50-90%); whitespace kills hits; needs measured hit rate | Marginal at Hiver sizes; defer claims |
| 8 | reasoning_effort | qwen3.8 none/default/low/medium/high; thinking 1.0/0.95 vs instruct 0.7/0.80 | Try none/low on draft leg (latency/cost experiment) |
| 9 | Function calling | GPT-5 only 15% at 20-call chains; stale-arg + sequence failures dominate | NO-tools posture justified; do not adopt |
| 10 | Judge small vs large | Kappa deflation 33-41pp; small judges most position-biased | Keep heuristic + gated LLM judge |
| 11 | Embeddings | $0.015-0.13/1M hosted; MiniLM fastest CPU, BGE-M3 free hybrid | Deferred; TF-IDF p50 7ms wins at 27k docs |
| 12 | Rerankers | Cohere v4 vs Jina v3.5 (63.2 BEIR, 131k ctx, 10M free) | First trial IF retrieval misses show in failures |
| 13 | Prompt Guard / Llama Guard | 22M $0.03/1M CPU L1 -> Guard 8B L2; live on Groq too | ADOPT 22M pre-filter (see top-3) |
| 14 | Granite Guardian | 4.1-8B Apache-2.0, BYOC + no-think yes/no, top-3 AggreFact | Eval-side scorer trial first |
| 15 | PII redaction | Presidio local sanitize+sweep is the chatbot pattern; Nightfall hosted alt | ADOPT Presidio pre-LLM (see top-3) |
| 16 | Fallback / circuit breaker | LiteLLM Router pattern + CLOSED->OPEN(5)->HALF-OPEN(60s) | Add counters/cooldown, no new dep (see top-3) |
| 17 | Rate-limit backoff | tenacity jitter + Retry-After canonical; retries burn RPM | NO retry in request path reaffirmed |
| 18 | Cost caps | Pre-flight estimate-vs-cap + ledger = ~30 lines, zero-dep | ADOPT CostCap + 256-out budget (see top-3) |
| 19 | Distillation | DistilBERT 40% smaller/60% faster/~97%; SetFit 8-shot ~= full-tune | Phase-2 intent path; never LLM-classify |
| 20 | Quantization | GGUF Q4_K_M universal CPU; AWQ best GPU; template still safest | Local LLM stays demo-only; not adopted |

## 3. Top-3 upgrades Hiver should adopt

### U1 — Pin strict:true + pre-flight cost cap on the draft path (effort: S)
- What: non-stream calls already send strict:true (now valid on qwen3.8-27b); add `CostCap(max_usd_per_call)` estimating `input + max_completion_tokens` before send, reject-to-template on breach; cut draft `max_completion_tokens` 2048 -> 256 (drafts are <=280 chars + JSON wrapper).
- Why: closes the two cheapest failure modes (schema drift, reasoning/prompt blowup) with zero deps; ~$0.0004/draft stays bounded even if thinking tokens spike.
- Fail-closed: any breach -> template with `groq_reason=cost-cap|validation-fail`, no secret in logs.
- Verify: unit test (cap trips on 2048-out estimate; passes on 256), smoke still 5/5 template keyless.

### U2 — Defense in depth: Prompt Guard 2 22M pre-filter + Presidio PII sanitize+sweep (effort: M)
- What: (a) Llama Prompt Guard 2 22M ($0.03/1M, CPU, 512 tok, chunk-long-prompts) before any LLM call; malicious -> escalate, never to LLM. (b) Presidio Analyzer+Anonymizer on inbound pre-LLM (email/phone/person + custom rail refs), reversible map held in-memory per request only; output sweep with re-redact policy (never restore PII into the draft).
- Why: replaces regex-only injection/PII handling; 22M is ~75% cheaper/faster than 86M and Groq-hosted as option; Presidio is local OSS, no data leaves for the guard itself.
- Fail-closed: guard error/uncertain -> escalate-with-packet; PII-dense inbound -> DM-redirect template (existing rule).
- Verify: extend `tests/test_brand_groq.py` + failure suite F4/F5/F8 with guard-on/off matrix; assert no PII reaches mocked client (inspect captured prompt).

### U3 — Breaker around the ordered chain (effort: S/M, no new dep)
- What: in-memory per-model counters in `src/groq_draft.py`: trip after N=5 consecutive 429/5xx (never on 400/401), cooldown 60s (skip leg while open, HALF-OPEN single probe), ordered chain qwen -> gpt-oss-120b -> template terminal; keep NO-retry-in-request-path (jittered 1s->2s->4s + Retry-After only in offline batch scripts).
- Why: matches LiteLLM Router semantics without the dependency; stops hammering a dead preview leg during Groq 429 storms (already observed live: qwen 429s -> gpt-oss fallback proven).
- Fail-closed: all-open -> template, `groq_reason=breaker-open`.
- Verify: unit test with mocked consecutive 429s (breaker opens, fallback serves, template after both open; recovery after cooldown).

## 4. Explicitly NOT adopted (with trigger to revisit)
- Provider switch (Cerebras/Together/Fireworks): revisit only if qwen preview discontinued AND gpt-oss quality drops on judge actionability.
- Hosted embeddings / reranker: revisit if failure analysis shows retrieval misses (recall@k) as top cause; first trial = Jina v3.5 or self-host BGE-M3.
- Function calling / agentic tools: never for money-affecting actions (Air Canada liability lesson); tools add compounding error with no Hiver task needing them.
- Local quantized LLM on request path: template dominates on determinism/cost for <=280ch grounded replies; GGUF small stays demo-mode only.
- LLM judge unblocking: stays gated (w-kappa>=0.60 + safety-recall>=0.90); Granite Guardian BYOC trialed eval-side first.
