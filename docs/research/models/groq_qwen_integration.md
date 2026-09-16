# Groq Qwen Integration — qwen/qwen3.8-27b (preview) → openai/gpt-oss-120b (production fallback) → template

**Date: 2026-09-11 | Scope: Hiver draft path only (`src/groq_draft.py` + `src/agent.py` signals) | All writes inside . only**
**Verified from official docs 2026-09-11:** `console.groq.com/docs/text-chat`, `/docs/structured-outputs`, `/docs/reasoning`, `/docs/models`, `/docs/rate-limits`, `/docs/prompt-caching`, `/docs/model/qwen/qwen3.8-27b`, `/docs/model/openai/gpt-oss-120b`, `groq/groq-python` README + `examples/chat_completion_streaming.py`.

## 0. Pinned model facts (official docs)

| Model | Status | Speed | Price / 1M | Context | Max output | Rate limits Free → Developer |
|---|---|---|---|---|---|---|
| `qwen/qwen3.8-27b` | **Preview** (eval only, may be discontinued without notice) | ~450+ tps | **$0.80 in / $4.00 out** | 131,042 | 16,384 | Free: 30 RPM / 1K RPD / 8K TPM / 2M TPD; Developer: check limits page (preview has no production SLA) |
| `openai/gpt-oss-120b` | **Production** | ~500 tps | **$0.15 in / $0.60 out**, cached in $0.075 | 131,072 | 65,536 | Free: 30 RPM / 1K RPD / 8K TPM / 200K TPD → Developer: **1K RPM / 250K TPM** |

Qwen3.8-27B card: dense 27B, 64 layers, hybrid Gated DeltaNet + Gated Attention, multimodal (text+images, 3 images max, 20 MB, 2048 tok/image), capabilities = Tool Use + JSON Object Mode + JSON Schema Mode + Reasoning + Vision. Thinking mode `reasoning_effort="default"`, instruct mode `"none"`, depth tune `"low"/"medium"/"high"`. Thinking-mode decoding: `temperature=1.0, top_p=0.95, top_k=20, min_p=0` (general) or `temperature=0.6` for precise coding; instruct: `temperature=0.7, top_p=0.80, presence_penalty=1.5`. History: only final outputs, no thinking content. User snippet (`temperature 0.6, max_completion_tokens 2048, top_p 0.95, reasoning_effort default, stream True`) = valid Qwen thinking-mode shape — matches Qwen3/official `temperature=0.6, top_p=0.95, top_k=20` guidance (DO NOT use greedy `temperature=0` in thinking mode — degradation + repetitions).

## 1. Exact call shape — qwen/qwen3.8-27b STREAMING (plain text, NO response_format)

Streaming + `response_format` = **400** (`response_format does not support streaming`, langchain-ai/langchain#23629; Groq docs: "Streaming and tool use are not currently supported with Structured Outputs"). So streaming path = plain text + code-side JSON/validation. `delta.content` may be `None` — guard it. Final chunk carries `finish_reason` + `x_groq.usage` (need `stream_options={"include_usage": true}` for usage chunk).

```python
import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])  # also honours GROQ_BASE_URL override

stream = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[
        {"role": "system", "content": (
            "You draft short UK customer-support replies for brand=virgin. "
            "Rules: <=280 chars, calm/plain, one next step, ask for DM on PII. "
            "Never invent times, platforms, or prices. If unsure, omit them. "
            'Return JSON only as {"draft_reply": "..."}.'
        )},
        {"role": "user", "content": (
            f"intent={intent}\n"
            f"inbound={inbound[:800]}\n"
            f"passages:\n- {ctx_block}\n"  # top-3 x 300 chars, or "(no passages; use safe generic help, no times/prices)"
            'Return {"draft_reply": "..."} (<=280 chars, no invented \u00a3 or HH:MM).'
        )},
    ],
    temperature=0.6,          # user snippet; Qwen thinking-mode canonical (0.6/0.95)
    max_completion_tokens=2048,  # covers reasoning + JSON; cap covers 16k max-out; see §5 pitfall (2048 generous for 280-char draft)
    top_p=0.95,               # user snippet
    reasoning_effort="default",  # Qwen3.8: none|default|low|medium|high; default = thinking on
    # reasoning_format="hidden",  # optional: hidden=final only, parsed=separate field, raw banned with JSON/tool use
    stop=None,                # or str | list[str]; NOT with response_format (see non-stream path)
    stream=True,
    # stream_options={"include_usage": True},  # uncomment to get x_groq.usage on final chunk
)

buf = []
finish = None
for chunk in stream:  # SSE: data: {json} ... data: [DONE]
    choice = chunk.choices[0]
    delta = choice.delta.content
    if delta is not None:      # REQUIRED guard — first/final chunks often None
        buf.append(delta)
    if choice.finish_reason:
        finish = choice.finish_reason
    # if getattr(chunk, "x_groq", None) and chunk.x_groq.usage: log usage (only on final chunk)
text = "".join(buf)
# then: strip ``` fences -> json.loads -> draft_reply -> validate_draft() (§3); finish=="length" => treat as truncated, fail closed
```

Async variant: `from groq import AsyncGroq; client = AsyncGroq(); stream = await client.chat.completions.create(..., stream=True); async for chunk in stream: ...` (identical chunk shape).

## 2. Exact call shape — qwen/qwen3.8-27b NON-STREAM JSON (strict:true, production-grade)

`strict:true` now lists `qwen/qwen3.8-27b` alongside `openai/gpt-oss-20b/120b` (structured-outputs page, fetched 2026-09-11 — closes the old "only GPT-OSS" gap in `docs/GROQ_UPGRADE.md` §3). Requirements: **all fields in `required` + `additionalProperties: false` on every object**. Never combine with `stream=True` or tools.

```python
import json
from groq import Groq
from pydantic import BaseModel

class DraftReply(BaseModel):
    draft_reply: str

client = Groq()  # GROQ_API_KEY from env
resp = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[
        {"role": "system", "content": "You draft short UK customer-support replies for brand=virgin. <=280 chars, calm/plain, one next step, DM on PII. Never invent times/platforms/prices. JSON only."},
        {"role": "user", "content": f"intent={intent}\ninbound={inbound[:800]}\npassages:\n- {ctx_block}\nReturn draft_reply <=280 chars."},
    ],
    temperature=0.6,
    max_completion_tokens=2048,
    top_p=0.95,
    reasoning_effort="default",
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "draft_reply_schema",
            "strict": True,  # constrained decoding on qwen3.8-27b — guaranteed schema adherence
            "schema": DraftReply.model_json_schema(),  # == {"type":"object","properties":{"draft_reply":{"type":"string"}},"required":["draft_reply"],"additionalProperties":False}
        },
    },
    stream=False,
)
obj = json.loads(resp.choices[0].message.content or "{}")  # still validate: refusal/length voids guarantee
draft = (obj.get("draft_reply") or "").strip()
ok, reason = validate_draft(draft, inbound, passages)  # §3; fail -> fallback chain §4
```

Note: docs examples omit `strict` on some pages (= defaults `false` = best-effort: valid JSON but may be wrong shape / 400). Always pass `strict: True` explicitly on these three models. For any other model, use `{"type":"json_object"}` + word "JSON" in prompt (syntax only, no schema) + server-side validation.

## 3. Validation rules — £/HH:MM grounding (keep `src/groq_draft.py:validate_draft` as-is)

1. Non-empty; `len(draft) <= 280` else `too-long` → fallback.
2. Extract `TOKEN_RE = £\s?[\d,]+(\.\d{1,2})? | \b\d{1,2}:\d{2}\b`. Every token must appear **verbatim (space-normalized)** in `inbound + top-3 passages` (text+clean). Else `ungrounded-token:<tok>` → fallback. Grounded £ (user wrote £12) passes — by design.
3. Check `finish_reason`: `length` = truncated JSON → fail closed (never parse-half). `refusal` → fail closed.
4. Strip ```json fences before `json.loads`; on parse fail, try raw-text draft then re-validate (current code does this — keep).
5. `info` dict never carries key/inbound (audited in tests). Log `draft_path=groq|template`, `groq_reason=ok|validation-fail:*|error|no-key|no-client`, `finish_reason`, `model`.

## 4. Fallback chain — qwen → gpt-oss-120b → template (fail-closed, one attempt per model in request path)

```
try qwen/qwen3.8-27b (reasoning_effort="default", temp 0.6/0.95, strict:true non-stream OR stream plain-text)
  → validate_draft OK? serve (draft_path=groq, model=qwen/...)
  → else try openai/gpt-oss-120b with REMAPPED effort (see below), temp 0.6/0.95, strict:true
    → validate_draft OK? serve (draft_path=groq-fallback, model=gpt-oss-120b)
    → else template (draft_path=template, groq_reason=validation-fail:*|error)
on 429/5xx: NO retry loop in request path — fail closed to next link immediately, surface groq_reason.
offline batch only: jittered backoff 1s→2s→4s on RateLimitError, respect `retry-after`, max 3, never on 400/401.
```

**Effort remap (load-bearing):** GPT-OSS supports ONLY `low|medium|high` (no `none`/`default`); Qwen3.6 supports ONLY `none|default`; Qwen3.8 supports all five (`none|default|low|medium|high`, `high` = native `xhigh`). So fallback call MUST translate: `qwen "default"` → `gpt-oss "medium"` (balanced; use `"low"` if p95 budget tight). Sending `default` to gpt-oss-120b = 400. `reasoning_format` (raw|parsed|hidden) is Qwen-only; GPT-OSS uses `include_reasoning: true/false` instead — do not send `reasoning_format` on fallback. `raw` is incompatible with JSON mode/tool use.

Why this order: qwen3.8 = best thinking quality for Hiver's short grounded drafts (GPQA 89.2, LiveCodeBench 90.3 per model card) at 450 tps; gpt-oss-120b = production SLA + 5× cheaper output + prompt caching; template = zero-cost deterministic guarantee (current default when no key).

## 5. Deltas vs OpenAI (webfetch summary — text-chat + structured-outputs)

- **`max_completion_tokens` vs `max_tokens`:** Groq docs use `max_completion_tokens` everywhere (text-chat examples: 1024); `groq-python` source marks `max_tokens` as **deprecated in favor of `max_completion_tokens`**. OpenAI history: `max_tokens` = billed+returned tokens; o1+ split to `max_completion_tokens` (includes invisible reasoning tokens). Rule: **always send `max_completion_tokens`** on Groq (both models accept it; 2048 fits qwen 16k + gpt-oss 65k caps). Never send both. Reasoning tokens consume this budget — 2048 is generous for a ≤280-char (~70 tok) draft + ~400 reasoning tokens; truncation shows as `finish_reason="length"`.
- **`reasoning_effort`:** OpenAI-style param but Groq-scoped matrix (see §4). Not an OpenAI chat-completions field for GPT-4-class; on Groq it is first-class with per-model enums. `temperature`+`reasoning_effort` interact: thinking mode needs 0.6/0.95, never 0.
- **`stop`:** Supported on Groq as `None | str | list[str]` (text-chat stop-sequence example `stop=", 6"`). **Unsupported together with `response_format`/`json_mode`** (LangChain: "`json_mode` does not support streaming responses stop sequences"; Groq 400 on `response_format`+`stream`). So: use `stop` only on streaming plain-text path; omit on JSON path.
- **Streaming shape:** identical SSE to OpenAI (`stream=True` → `Stream[ChatCompletionChunk]`, `choices[0].delta.content`, `data: [DONE]`), plus Groq extras: `delta.reasoning`, `message.reasoning` / `executed_tools` (Compound/GPT-OSS), `x_groq.id` (first+final chunk) + `x_groq.usage` (final, needs `stream_options.include_usage`). OpenAI-compatible client (`OpenAI(base_url="https://api.groq.com/openai/v1")`) works, but native `groq` SDK (`pip install groq`, `Groq()`/`AsyncGroq()`, `GROQ_API_KEY` default, `max_retries=2` auto on 429/5xx) is recommended.
- **Structured outputs:** OpenAI `json_schema/strict:true` maps 1:1, but Groq enforces **strict:true only on 3 models** (gpt-oss-20b/120b + qwen3.8-27b as of fetch; older secondary sources list only 2 — stale). Best-effort `strict:false` = valid JSON, wrong-shape possible + 400s. JSON Object Mode needs literal "JSON" in prompt. Refusal/length voids guarantee on both providers — always code-validate.

## 6. Rate limits — 1K RPM handling + backoff (Hiver policy)

Free: 30 RPM / 1K RPD binds first (≈1 req/2s sustained); Developer: 1K RPM / 250K TPM on gpt-oss-120b. Hiver drafts ≈600 in-tokens → TPM never binds before RPM on free (≈18K TPM at 30 RPM). Headers on every response: `x-ratelimit-*` + `retry-after` (429 only). SDK auto-retries 2× — disable in request path (`max_retries=0`) to keep fail-closed latency.

Policy (already in `docs/GROQ_UPGRADE.md` §5, reaffirmed): **one attempt per model in request path, fail closed to next link; jittered backoff reserved for offline batch.** For 1K RPM Developer: client-side token bucket (~900 RPM safety margin), concurrency cap = RPM × p50(s)/60 (e.g. 1s p50 → ~15 concurrent at 900 RPM), queue don't busy-retry, alert if retry rate >5%. Distinguish RPM vs TPM 429s from error body (`tokens` vs `requests`) — TPM-429 = shrink context (fewer passages), RPM-429 = pace.

## 7. Prompt caching (only gpt-oss-120b leg benefits)

Auto, zero code changes, no fee. **Only `openai/gpt-oss-20b/120b/safeguard-20b`** — qwen3.8-27b NOT cached. 50% off cached input ($0.075 vs $0.15 on 120b), exact-prefix match from request start, min 128–1024 tokens (model-dependent), 2h TTL, cached tokens excluded from rate limits, not stackable with Batch 50%. Hiver shape (static system + fixed template + brand preamble, variable inbound+passages at END) is cache-optimal on the fallback leg — keep static prefix byte-identical to maximize hits; check `usage.prompt_tokens_details.cached_tokens`.

## 8. Cost per 1k reqs (measured math, assumptions explicit)

Assumes Hiver token shape: ~600 in (800-char inbound + 3×300-char passages + system) + ~70 out (≤280-char draft). Reasoning adds ~400 tokens when thinking on.

| Leg | No-reasoning (70 out) | With reasoning (~470 out) |
|---|---|---|
| qwen3.8-27b $0.80/$4.00 | $0.00048 + $0.00028 = **$0.00076/req → $0.76 / 1k** | $0.00048 + $0.00188 = **$0.00236/req → $2.36 / 1k** |
| gpt-oss-120b $0.15/$0.60 | $0.00009 + $0.000042 = **$0.00013/req → $0.13 / 1k** | $0.00009 + $0.000282 = **$0.00037/req → $0.37 / 1k** (+ cache hits cut input half → ~$0.09–0.33/1k effective) |

Context: old llama-3.3-70b $0.59/$0.79 ≈ $0.40/1k (no reasoning). Qwen preview output is 5× gpt-oss output — keep fallback hot. Eval gates never call Groq in bulk (keyless default).

## 9. Pitfalls (the ones that 400 in prod)

1. `stream=True` + `response_format` → 400. Two paths, never merged.
2. `reasoning_effort="default"` → gpt-oss-120b → 400. Remap to `medium` (or `low`).
3. `reasoning_format="raw"` + JSON/tool use → unsupported. Use `hidden`/`parsed` or omit.
4. `temperature=0` in Qwen thinking mode → degradation/repetition. Keep 0.6/0.95 per snippet.
5. `delta.content is None` unguarded → `TypeError` on concat. Guard every chunk.
6. `max_completion_tokens` too small (reasoning eats budget) → `finish_reason=length` + empty/partial JSON. 2048 is safe; alert at 80% usage.
7. `strict:true` without all-`required` + `additionalProperties:false` → 400. Pydantic `model_json_schema()` already emits both — use it.
8. Preview status: qwen3.8-27b may be discontinued without notice — fallback chain is not optional.
9. `stop` + JSON path → ignored/400. `stop` only on streaming plain-text.
10. History pollution: never feed back thinking content (Qwen best practice) — store only `draft_reply`.
11. Cached-rate math on wrong leg: prompt caching does NOT apply to qwen — don't budget it there.

## 10. Sources (12 websearch + 2 webfetch, 2026-09-11)

Searches: (1) streaming delta.content SSE; (2) structured outputs strict per-model; (3) reasoning_effort model matrix; (4) groq-sdk python streaming; (5) rate limits RPM/TPM backoff; (6) prompt caching; (7) qwen3.8-27b pricing/ctx; (8) gpt-oss-120b pricing/ctx; (9) max_completion_tokens vs max_tokens; (10) stop + streaming/structured-output exclusion; (11) Qwen thinking decoding 0.6/0.95; (12) Developer 1K RPM/250K TPM. Fetches: `https://console.groq.com/docs/text-chat` (stream/stop/async/max_completion_tokens), `https://console.groq.com/docs/structured-outputs` (strict:true now incl. qwen3.8-27b; streaming+tools excluded). Cross-checked: `/docs/reasoning`, `/docs/models`, `/docs/rate-limits`, `/docs/prompt-caching`, model cards, groq-python README/examples, langchain#23629, Vercel AI SDK Groq provider.
