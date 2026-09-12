"""Groq live drafter (openai/gpt-oss-20b primary + qwen/qwen3.8-27b conditional fallback) + validation gate.

Fail-closed to template: (None, info) on no-key / no-client / error / validation-fail.
Key via GROQ_API_KEY env only — never committed (see .env.example).
Strict constrained decoding (`strict:true`) is supported ONLY on
openai/gpt-oss-20b, openai/gpt-oss-120b and qwen/qwen3.8-27b
(console.groq.com/docs/structured-outputs, verified 2026-09-12) — both legs
below are in that set, so strict:true is always valid here. Streaming +
tool-use are NOT supported with Structured Outputs (plain-text stream path only).
Instructor path: `instructor.from_provider("groq/<model>")` (instructor==1.17.0)
with graceful ImportError fallback to the existing JSON-schema parsing
(no hard dependency at import time).
Research: research/models/groq_qwen_integration.md (stream+response_format=400 -> two paths;
reasoning_effort default; max_completion_tokens; £/HH:MM grounding).
"""
import json
import os
import re

# Phase 4A (additive): sandbox untrusted passages; resilience (breaker+retry).
try:
    from . import sandbox as _sandbox
except Exception:
    _sandbox = None
try:
    from . import resilience as _resilience
except Exception:
    _resilience = None

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
# D1 (PLAN_V2, locked 2026-09-12): primary = openai/gpt-oss-20b (production,
# $0.075/$0.30 per M, ~1000 t/s, strict:true); fallback = qwen/qwen3.8-27b
# (preview, conditional arm only — may be discontinued without notice).
# llama-3.3-70b-versatile DROPPED (Enterprise/ContactSales pricing).
GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_FALLBACK_MODEL = "qwen/qwen3.8-27b"
MAX_DRAFT_CHARS = 280

PRICE_RE = re.compile(r"£")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}\b")
TOKEN_RE = re.compile(r"£\s?[\d,]+(?:\.\d{1,2})?|\b\d{1,2}:\d{2}\b")
URL_RE = re.compile(r"https?://\S+|t\.co/\S+|www\.\S+")
FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.S)


def _api_key():
    k = os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY")
    return k.strip() if k and k.strip() else None


def validate_draft(draft, inbound, passages):
    if not draft or not draft.strip():
        return False, "empty"
    d = draft.strip().replace(" ", " ").replace(" ", " ")
    if len(d) > MAX_DRAFT_CHARS:
        return False, "too-long"
    toks = TOKEN_RE.findall(d)
    if toks:
        sources = (inbound or "") + "\n"
        try:
            for p in (passages or [])[:3]:
                if isinstance(p, dict):
                    sources += (p.get("text") or "") + "\n" + (p.get("clean") or "") + "\n"
                elif isinstance(p, str):
                    sources += p + "\n"
        except Exception:
            sources = inbound or ""
        for t in toks:
            t_norm = t.strip()
            if t_norm not in sources and t_norm.replace(" ", "") not in sources.replace(" ", ""):
                return False, f"ungrounded-token:{t_norm[:16]}"
    # URLs: model loves inventing t.co links — any URL must be verbatim in sources
    for u in URL_RE.findall(d):
        if u not in ((inbound or "") + "\n" + "\n".join(
                ((p.get("text") or "") if isinstance(p, dict) else str(p)) for p in (passages or [])[:3])):
            return False, f"ungrounded-url:{u[:24]}"
    return True, "ok"


def _prompts(intent, inbound, passages, brand):
    # Phase 4A: sandbox retrieved passages as untrusted data.
    try:
        if _sandbox is not None:
            ctx_block = _sandbox.build_context(passages, k=3)
        else:
            raise RuntimeError("no-sandbox")
    except Exception:
        ctx = []
        for p in (passages or [])[:3]:
            t = (p.get("text") or p.get("clean") or "")[:300] if isinstance(p, dict) else str(p)[:300]
            if t.strip():
                ctx.append(t.strip())
        ctx_block = "\n- ".join(ctx) if ctx else "(no passages; safe generic help, no times/prices)"
    system = (
        f"You draft short UK customer-support replies for brand={brand}. "
        "Rules: <=280 chars, calm/plain, one next step, ask for DM on PII. "
        "Never invent times, platforms, prices, or URLs/links. If unsure, omit them. "
        'Return JSON only as {"draft_reply": "..."}.'
    )
    try:
        if _sandbox is not None:
            system = _sandbox.harden_system_prompt(system)
    except Exception:
        pass
    user = (
        f"intent={intent}\n"
        f"inbound={(inbound or '')[:800]}\n"
        f"passages:\n- {ctx_block}\n"
        'Return {"draft_reply": "..."} (<=280 chars, no invented £, HH:MM, or links).'
    )
    return system, user


def _client():
    try:
        from groq import Groq
        return Groq(), "groq-sdk"
    except ImportError:
        try:
            from openai import OpenAI
            key = _api_key()
            return OpenAI(api_key=key, base_url=GROQ_BASE_URL), "openai-compat"
        except Exception:
            return None, "no-client"
    except Exception:
        return None, "no-client"


def _draft_json_schema():
    """Strict JSON-schema shape for {"draft_reply": str} (offline-validatable).

    Valid ONLY with strict:true on openai/gpt-oss-20b, openai/gpt-oss-120b and
    qwen/qwen3.8-27b (constrained decoding). Both GROQ_MODEL legs are in that
    set — never send strict:true to any other model.
    """
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "draft_reply_schema",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"draft_reply": {"type": "string"}},
                "required": ["draft_reply"],
                "additionalProperties": False,
            },
        },
    }


def _try_instructor_draft(model, sys_prompt, user_prompt):
    """Instructor from_provider draft for one model.

    Returns (draft|None, via|None, usage). ImportError (or missing pydantic) ->
    (None, None, None) so the caller falls back to the existing JSON parsing.
    Any other exception -> (None, "error:<Type>", empty-usage) and the caller
    still tries the JSON path for the same model before the next fallback leg.
    No hard dependency at import time; no secrets in outputs.
    """
    try:
        import instructor  # noqa: F401  (optional dep, instructor==1.17.0)
    except ImportError:
        return None, None, None
    try:
        from pydantic import BaseModel

        class _DraftReply(BaseModel):
            draft_reply: str

        client = instructor.from_provider(f"groq/{model}")
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.6,
            max_completion_tokens=256,
            top_p=0.95,
            response_model=_DraftReply,
            strict=True,
            max_retries=1,
        )
        draft = (getattr(resp, "draft_reply", "") or "").strip()
        return draft, "instructor", _empty_usage()
    except ImportError:
        return None, None, None
    except Exception as e:
        return None, f"error:{type(e).__name__}", _empty_usage()


def _empty_usage():
    return {"prompt_tokens": None, "completion_tokens": None}


def _extract_usage(resp):
    """Best-effort token usage from Groq/OpenAI response. Never raises, never includes secrets."""
    try:
        u = getattr(resp, "usage", None)
        if u is None:
            return _empty_usage()
        if isinstance(u, dict):
            pt = u.get("prompt_tokens")
            ct = u.get("completion_tokens")
        else:
            pt = getattr(u, "prompt_tokens", None)
            ct = getattr(u, "completion_tokens", None)
        try:
            pt = int(pt) if pt is not None else None
        except Exception:
            pt = None
        try:
            ct = int(ct) if ct is not None else None
        except Exception:
            ct = None
        return {"prompt_tokens": pt, "completion_tokens": ct}
    except Exception:
        return _empty_usage()


def draft_with_groq(intent, inbound, passages, brand="virgin"):
    """Non-streaming Groq draft. Returns (text|None, info)."""
    info_base = {"brand": brand, "intent": intent, "model": GROQ_MODEL}
    # Exact strings that would be sent (computed once so info matches the request).
    try:
        _sys_prompt, _user_prompt = _prompts(intent, inbound, passages, brand)
    except Exception:
        _sys_prompt, _user_prompt = "", ""
    if not _api_key():
        return None, {**info_base, "reason": "no-key", "draft_path": "template",
                      "sys_prompt": "", "user_prompt": "", "usage": _empty_usage()}
    # Phase 4A: breaker-open short-circuit (bounded latency, template fallback).
    try:
        if _resilience is not None and _resilience.is_breaker_open():
            return None, {**info_base, "reason": "breaker-open", "draft_path": "template",
                          "sys_prompt": _sys_prompt, "user_prompt": _user_prompt, "usage": _empty_usage()}
    except Exception:
        pass
    client, via = _client()
    if client is None:
        return None, {**info_base, "reason": "no-client", "draft_path": "template",
                      "sys_prompt": "", "user_prompt": "", "usage": _empty_usage()}
    last = "error"
    for model in (GROQ_MODEL, GROQ_FALLBACK_MODEL):
        # 1) Instructor structured path (optional dep; ImportError -> JSON below).
        try:
            _ins_draft, _ins_via, _ins_usage = _try_instructor_draft(model, _sys_prompt, _user_prompt)
        except Exception:
            _ins_draft, _ins_via, _ins_usage = None, None, None
        if _ins_draft:
            ok, reason = validate_draft(_ins_draft, inbound, passages)
            if not ok:
                return None, {**info_base, "model": model, "reason": f"validation-fail:{reason}", "draft_path": "template",
                              "sys_prompt": _sys_prompt, "user_prompt": _user_prompt, "usage": _ins_usage or _empty_usage()}
            return _ins_draft, {**info_base, "model": model, "reason": "ok", "draft_path": "groq", "via": _ins_via or "instructor",
                                "sys_prompt": _sys_prompt, "user_prompt": _user_prompt, "usage": _ins_usage or _empty_usage()}
        # 2) Existing JSON-schema path (fallback when Instructor is absent or errored).
        # Phase 4A: breaker-gated + 429/5xx-only retry (<=3) via resilience wrapper.
        try:
            try:
                _create = client.chat.completions.create
                if _resilience is not None:
                    resp = _resilience.call_groq_with_resilience(
                        _create,
                        model=model,
                        messages=[
                            {"role": "system", "content": _sys_prompt},
                            {"role": "user", "content": _user_prompt},
                        ],
                        temperature=0.6,
                        max_completion_tokens=256,
                        top_p=0.95,
                        response_format=_draft_json_schema(),
                        stop=None,
                    )
                else:
                    raise RuntimeError("_no_resilience_fallback")
            except Exception as _w:
                # CircuitBreakerError -> fail closed immediately (template).
                try:
                    import pybreaker as _pb
                    if isinstance(_w, _pb.CircuitBreakerError):
                        return None, {**info_base, "reason": "breaker-open", "draft_path": "template",
                                      "sys_prompt": _sys_prompt, "user_prompt": _user_prompt, "usage": _empty_usage()}
                except Exception:
                    if "CircuitBreaker" in type(_w).__name__ or "breaker-open" in str(_w).lower():
                        return None, {**info_base, "reason": "breaker-open", "draft_path": "template",
                                      "sys_prompt": _sys_prompt, "user_prompt": _user_prompt, "usage": _empty_usage()}
                if _resilience is None and "_no_resilience_fallback" in str(_w):
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": _sys_prompt},
                            {"role": "user", "content": _user_prompt},
                        ],
                        temperature=0.6,
                        max_completion_tokens=256,
                        top_p=0.95,
                        response_format=_draft_json_schema(),
                        stop=None,
                    )
                else:
                    raise
            content = resp.choices[0].message.content or ""
            try:
                draft = (json.loads(content).get("draft_reply") or "").strip()
            except Exception:
                draft = FENCE_RE.sub("", content.strip()).strip()
            ok, reason = validate_draft(draft, inbound, passages)
            if not ok:
                return None, {**info_base, "model": model, "reason": f"validation-fail:{reason}", "draft_path": "template",
                              "sys_prompt": _sys_prompt, "user_prompt": _user_prompt, "usage": _extract_usage(resp)}
            return draft, {**info_base, "model": model, "reason": "ok", "draft_path": "groq", "via": via,
                           "sys_prompt": _sys_prompt, "user_prompt": _user_prompt, "usage": _extract_usage(resp)}
        except Exception as e:
            last = f"{type(e).__name__}"
            continue
    return None, {**info_base, "reason": "error", "error_type": last, "draft_path": "template",
                  "sys_prompt": _sys_prompt, "user_prompt": _user_prompt, "usage": _empty_usage()}


def stream_groq_draft(intent, inbound, passages, brand="virgin"):
    """Streaming Groq draft (plain text + parse; stream+response_format=400 so NO response_format here).
    Yields (chunk_text|None, done_info|None). Final yield carries (None, info) with full draft in info['draft'].
    """
    info_base = {"brand": brand, "intent": intent, "model": GROQ_MODEL}
    if not _api_key():
        yield None, {**info_base, "reason": "no-key", "draft_path": "template", "draft": None}
        return
    # Phase 4A: breaker-open short-circuit (bounded latency, template fallback).
    try:
        if _resilience is not None and _resilience.is_breaker_open():
            yield None, {**info_base, "reason": "breaker-open", "draft_path": "template", "draft": None}
            return
    except Exception:
        pass
    client, via = _client()
    if client is None:
        yield None, {**info_base, "reason": "no-client", "draft_path": "template", "draft": None}
        return
    system, user = _prompts(intent, inbound, passages, brand)
    kwargs = dict(
        model=GROQ_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.6,
        max_completion_tokens=2048,
        top_p=0.95,
        reasoning_effort="default",
        stop=None,
        stream=True,
    )
    try:
        stream = client.chat.completions.create(**kwargs)
    except Exception:
        # Some SDK/server combos reject reasoning_effort -> retry without it, then fallback model
        try:
            kwargs.pop("reasoning_effort", None)
            stream = client.chat.completions.create(**kwargs)
        except Exception:
            pass
        else:
            model_used = GROQ_MODEL
            buf = []
            try:
                for chunk in stream:
                    try:
                        c = chunk.choices[0]
                    except Exception:
                        continue
                    piece = None
                    try:
                        if c.delta and c.delta.content is not None:
                            piece = c.delta.content
                    except Exception:
                        piece = None
                    if piece:
                        buf.append(piece)
                        yield piece, None
            except Exception as e:
                yield None, {**info_base, "model": model_used, "reason": "error", "error_type": type(e).__name__, "draft_path": "template", "draft": None}
                return
            raw = FENCE_RE.sub("", "".join(buf).strip()).strip()
            try:
                obj = json.loads(raw)
                draft = (obj.get("draft_reply") or "").strip() if isinstance(obj, dict) else raw
            except Exception:
                draft = raw
            ok, reason = validate_draft(draft, inbound, passages)
            if not ok:
                yield None, {**info_base, "model": model_used, "reason": f"validation-fail:{reason}", "draft_path": "template", "draft": None}
            else:
                yield None, {**info_base, "model": model_used, "reason": "ok", "draft_path": "groq", "via": via, "draft": draft}
            return
        try:
            kwargs["model"] = GROQ_FALLBACK_MODEL
            stream = client.chat.completions.create(**kwargs)
            model_used = GROQ_FALLBACK_MODEL
        except Exception as e2:
            yield None, {**info_base, "reason": "error", "error_type": type(e2).__name__, "draft_path": "template", "draft": None}
            return
    else:
        model_used = GROQ_MODEL
    buf = []
    try:
        for chunk in stream:
            try:
                c = chunk.choices[0]
            except Exception:
                continue
            piece = None
            try:
                if c.delta and c.delta.content is not None:
                    piece = c.delta.content
            except Exception:
                piece = None
            if piece:
                buf.append(piece)
                yield piece, None
    except Exception as e:
        yield None, {**info_base, "model": model_used, "reason": "error", "error_type": type(e).__name__, "draft_path": "template", "draft": None}
        return
    raw = FENCE_RE.sub("", "".join(buf).strip()).strip()
    try:
        obj = json.loads(raw)
        draft = (obj.get("draft_reply") or "").strip() if isinstance(obj, dict) else raw
    except Exception:
        draft = raw
    ok, reason = validate_draft(draft, inbound, passages)
    if not ok:
        yield None, {**info_base, "model": model_used, "reason": f"validation-fail:{reason}", "draft_path": "template", "draft": None}
    else:
        yield None, {**info_base, "model": model_used, "reason": "ok", "draft_path": "groq", "via": via, "draft": draft}
