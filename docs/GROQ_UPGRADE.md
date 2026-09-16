# Groq Upgrade — keyless prototype → live drafter (behind validation gate)

Status: prototype, no key required. Template path is the default; Groq fails closed to template.
Code: `src/groq_draft.py` (drafter) + `src/agent.py` (`AppleAgent.handle`, `draft_path` in signals).
Tests: `tests/test_brand_groq.py` (no-key, validation-fail, error→template). Smoke: `scripts/groq_smoke.py`.

## 1. Env setup (Windows PowerShell)

```powershell
# Keyless (default, all gates pass): ensure neither var is set
Remove-Item Env:\GROQ_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:\OPENAI_API_KEY -ErrorAction SilentlyContinue

# Live (key arrives later): env only, never in code, never logged
$env:GROQ_API_KEY="gsk_..."   # preferred; OPENAI_API_KEY is fallback in src/groq_draft.py:_api_key()
$env:PYTHONPATH="C:\Hiver"
python C:\Hiver\scripts\groq_smoke.py   # keyed run: expect mix of groq|template
python -m pytest C:\Hiver\tests -q
```

Client (already wired, OpenAI-compatible):

```python
from openai import OpenAI
client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
```

Notes from docs (Sep 2026): Groq also ships a native `groq` SDK (`GROQ_API_KEY` default, `GROQ_BASE_URL` override,
auto-retry 2× on 429/5xx). We stay on the `openai`-compatible client — one dep, no code change if provider swaps.

## 2. Model + decoding

- Model: `openai/gpt-oss-20b` (historical: `llama-3.3-70b-versatile`, retired 2026-09-12) (70B-class context, ~280 tok/s per Groq docs, ~394 tok/s
  third-party bench). Pinned in `GROQ_MODEL` + per-brand `groq_model` config.
- `temperature=0`, `max_tokens=256`, passages truncated to top-3 × 300 chars, inbound to 800 chars.
- System prompt: UK support, brand param, ≤280 chars, calm/plain, one next step, DM on PII, never invent
  times/platforms/prices. User prompt echoes `intent + inbound + passages`, demands JSON-only.

## 3. Schema (best-effort — validate server-side, always)

```json
{"type": "json_schema", "json_schema": {"name": "draft_reply_schema", "strict": false,
 "schema": {"type": "object", "properties": {"draft_reply": {"type": "string"}},
 "required": ["draft_reply"], "additionalProperties": false}}}
```

Why `strict: false`: per Groq Structured-Outputs docs, constrained `strict: true` is only guaranteed on select
models (GPT-OSS 20B/120B); on 70B-versatile `false` is best-effort — it may return valid-JSON/wrong-shape or HTTP 400
`Generated JSON does not match the expected schema`. So we treat JSON mode as a hint, not a contract:

1. `json.loads(content)` → `draft_reply`; fallback: strip ``` fences, retry parse; else raw text.
2. `validate_draft()` gate (see §4) — fail → `(None, reason=validation-fail:*)` → template.
3. Any exception → `(None, reason=error)` → template. No key / no `openai` lib → `no-key` / `no-client` → template.
4. `info` dict never carries key/inbound text (audited in tests).

Pitfalls handled: high-temp malformed JSON (we pin temp 0), `finish_reason=length` truncation (we cap
`max_tokens=256` for a ≤280-char reply and re-validate length), code-fenced JSON, schema drift (Pydantic-style
shape check via required-key lookup, not blind trust).

## 4. Validation rules (`validate_draft`)

- Non-empty, `len(draft) ≤ 280` (`too-long` → template).
- Grounding: every `£[amount]` / `HH:MM` token in the draft must appear verbatim (space-normalized) in
  `inbound + top-3 passages`; else `ungrounded-token:<tok>` → template. Grounded £ (e.g. user wrote £12) passes.
- Agent records `signals["draft_path"] = groq|template` plus `groq_reason` (no-key|no-client|ok|validation-fail:*|error).

## 5. Cost / latency expectation

- Price (Sep 2026): **$0.59 / 1M input, $0.79 / 1M output** (Batch API −50%, cache −50%, stackable — not used here).
- Per draft ≈ ~600 input + ~60 output tokens ≈ **~$0.0004**. Eval gates never call Groq in bulk.
- Latency: reference notebook completion_time **0.96 s** for a 70B-versatile chat completion; expect
  ~1 s TTFT-class per draft call. Groq path is **never on the critical path** — template serves on any failure.
- Rate limits: free tier **~30 RPM**; SDK default `max_retries=2` with backoff; 429 exposes `retry-after`.
  Policy: **no retry loop in the request path** — one attempt, fail closed to template, surface `groq_reason`.
  Retry-with-jitter (`1s→2s→4s`, `RateLimitError`-only, never on 400/401) is reserved for offline batch use.

## 6. Rollback (= unset key)

```powershell
Remove-Item Env:\GROQ_API_KEY -ErrorAction SilentlyContinue
$env:PYTHONPATH="C:\Hiver"
python C:\Hiver\scripts\groq_smoke.py   # must print: all cases draft_path=template
python -m pytest C:\Hiver\tests -q      # must pass
```

API/UI check: `/predict` responses show `draft_path=template`, `groq_reason=no-key`. No deploy needed —
code path is identical, only the env var changes.

## 7. When the key arrives (checklist)

1. `$env:GROQ_API_KEY="gsk_..."` in session only (CI: secret store, never repo).
2. `python scripts/groq_smoke.py` — confirm some `draft_path=groq`, no `too-long`, no exceptions.
3. `python -m pytest tests -q` — all green including the 2 mocked fail-closed tests.
4. Spot-check 20 drafts: validation-fail rate, £/time grounding precision, ≤280-char compliance.
5. Watch 429s: if retries >5% of calls, cap concurrency / token-bucket (~28 RPM safety margin) or upgrade tier.
6. Optional: `evaluation/judge.py` LLM hook (`gpt-4o-mini`) stays separate — do not route judge traffic via Groq key.
