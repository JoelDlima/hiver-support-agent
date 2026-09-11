"""Groq live drafter (qwen/qwen3.8-27b per user) + fallback + validation gate.

Fail-closed to template: (None, info) on no-key / no-client / error / validation-fail.
Key via GROQ_API_KEY env only — never committed (see .env.example).
Research: research/models/groq_qwen_integration.md (stream+response_format=400 -> two paths;
reasoning_effort default; max_completion_tokens; £/HH:MM grounding).
"""
import json
import os
import re

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "qwen/qwen3.8-27b"
GROQ_FALLBACK_MODEL = "openai/gpt-oss-120b"
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


def draft_with_groq(intent, inbound, passages, brand="virgin"):
    """Non-streaming Groq draft. Returns (text|None, info)."""
    info_base = {"brand": brand, "intent": intent, "model": GROQ_MODEL}
    if not _api_key():
        return None, {**info_base, "reason": "no-key", "draft_path": "template"}
    client, via = _client()
    if client is None:
        return None, {**info_base, "reason": "no-client", "draft_path": "template"}
    for model in (GROQ_MODEL, GROQ_FALLBACK_MODEL):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _prompts(intent, inbound, passages, brand)[0]},
                    {"role": "user", "content": _prompts(intent, inbound, passages, brand)[1]},
                ],
                temperature=0.6,
                max_completion_tokens=256,
                top_p=0.95,
                response_format={
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
                },
                stop=None,
            )
            content = resp.choices[0].message.content or ""
            try:
                draft = (json.loads(content).get("draft_reply") or "").strip()
            except Exception:
                draft = FENCE_RE.sub("", content.strip()).strip()
            ok, reason = validate_draft(draft, inbound, passages)
            if not ok:
                return None, {**info_base, "model": model, "reason": f"validation-fail:{reason}", "draft_path": "template"}
            return draft, {**info_base, "model": model, "reason": "ok", "draft_path": "groq", "via": via}
        except Exception as e:
            last = f"{type(e).__name__}"
            continue
    return None, {**info_base, "reason": "error", "error_type": last, "draft_path": "template"}


def stream_groq_draft(intent, inbound, passages, brand="virgin"):
    """Streaming Groq draft (plain text + parse; stream+response_format=400 so NO response_format here).
    Yields (chunk_text|None, done_info|None). Final yield carries (None, info) with full draft in info['draft'].
    """
    info_base = {"brand": brand, "intent": intent, "model": GROQ_MODEL}
    if not _api_key():
        yield None, {**info_base, "reason": "no-key", "draft_path": "template", "draft": None}
        return
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
