"""FastAPI for Hiver support agent (VirginTrains primary, AppleSupport kept). Stateless, CPU-only + optional Groq."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import collections
import datetime
import json
import logging
import re
import threading
import time, uuid
from pathlib import Path
from src.agent import AppleAgent
from src.retriever import Retriever
from src import brands as brands_mod

# ---- Phase 4A (additive): hardening + observability imports (fail-soft) ----
try:
    from slowapi import Limiter
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    _SLOWAPI_OK = True
except Exception:
    Limiter = None
    SlowAPIMiddleware = None
    get_remote_address = None
    RateLimitExceeded = None
    _SLOWAPI_OK = False
try:
    from starlette.exceptions import HTTPException as StarletteHTTPException
except Exception:
    StarletteHTTPException = None
try:
    from fastapi.exceptions import RequestValidationError
except Exception:
    RequestValidationError = None
try:
    from src import tracing as _tracing
except Exception:
    _tracing = None

logger = logging.getLogger("hiver")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)
MAX_CHARS = 2000

# Per-brand metrics: {brand: {predict_count, escalate_count, auto_count, total_latency_ms, latencies[]}}
# latencies = reservoir of last 200 end-to-end ms for honest p50/p95 (avg lies under skew).
def _fresh_counters():
    return {"predict_count": 0, "escalate_count": 0, "auto_count": 0, "total_latency_ms": 0.0, "latencies": []}


def _record_latency(brand: str, latency_ms: float, decision: str):
    with _metrics_lock:
        if brand not in _metrics_per_brand:
            _metrics_per_brand[brand] = _fresh_counters()
        c = _metrics_per_brand[brand]
        c["predict_count"] += 1
        c["total_latency_ms"] += latency_ms
        c["latencies"].append(float(latency_ms))
        if len(c["latencies"]) > 200:
            c["latencies"] = c["latencies"][-200:]
        if decision == "escalate":
            c["escalate_count"] += 1
        else:
            c["auto_count"] += 1

_metrics_per_brand = {b: _fresh_counters() for b in brands_mod.list_brands()}
_metrics_lock = threading.Lock()

# ---- Live-proof: inspect store (thread-safe, cap 200, evict oldest) ----
_INSPECT_MAX = 200
_inspect_store: dict = {}
_inspect_lock = threading.Lock()


def _store_inspect(record: dict):
    rid = (record or {}).get("request_id")
    if not rid:
        return
    with _inspect_lock:
        if rid in _inspect_store:
            _inspect_store.pop(rid, None)
        else:
            while len(_inspect_store) >= _INSPECT_MAX:
                try:
                    oldest = next(iter(_inspect_store))
                except StopIteration:
                    break
                _inspect_store.pop(oldest, None)
        _inspect_store[rid] = record


def _get_inspect(rid: str):
    with _inspect_lock:
        return _inspect_store.get(rid)


# ---- Live-proof: log tail (deque maxlen 300, thread-safe append) ----
_log_tail: collections.deque = collections.deque(maxlen=300)
_log_lock = threading.Lock()
_log_seq = 0


class _TailHandler(logging.Handler):
    def emit(self, record):
        global _log_seq
        try:
            msg = self.format(record)
            if "gsk_" in msg:
                msg = re.sub(r"gsk_[A-Za-z0-9_\-]+", "[REDACTED]", msg)
            with _log_lock:
                _log_tail.append(msg)
                _log_seq += 1
        except Exception:
            pass


_tail_handler = _TailHandler()
_tail_handler.setFormatter(logging.Formatter("%(message)s"))
_hiver_log = logging.getLogger("hiver")
if not any(isinstance(h, _TailHandler) for h in _hiver_log.handlers):
    _hiver_log.addHandler(_tail_handler)
try:
    _hiver_log.setLevel(logging.INFO)
except Exception:
    pass


def _collect_passages(agent, text, k=5):
    try:
        retr = getattr(agent, "retriever", None)
        if retr is None:
            return []
        res = retr.query(text or "", k=k)
        out = []
        for p in (res or [])[:k]:
            try:
                out.append({
                    "tweet_id": str(p.get("tweet_id", "")),
                    "score": round(float(p.get("score", 0.0)), 4),
                    "text": (p.get("text") or "")[:200],
                })
            except Exception:
                continue
        return out
    except Exception:
        return []


def _build_llm_block(result, sig):
    try:
        ginfo = getattr(result, "groq_info", {}) or {}
    except Exception:
        ginfo = {}
    if not isinstance(ginfo, dict):
        ginfo = {}
    if not isinstance(sig, dict):
        sig = {}
    draft_path = str(sig.get("draft_path") or ginfo.get("draft_path") or "template")
    groq_reason = ""
    try:
        if sig.get("groq_reason"):
            groq_reason = str(sig.get("groq_reason"))[:64]
        elif ginfo.get("reason") and ginfo.get("reason") != "ok":
            groq_reason = str(ginfo.get("reason"))[:64]
    except Exception:
        groq_reason = ""
    try:
        model = str(ginfo.get("model") or "qwen/qwen3.8-27b")
    except Exception:
        model = "qwen/qwen3.8-27b"
    if draft_path == "groq":
        try:
            system = str(ginfo.get("sys_prompt") or "")
        except Exception:
            system = ""
        try:
            user = str(ginfo.get("user_prompt") or "")[:2000]
        except Exception:
            user = ""
        completion = result.draft_reply
        usage = ginfo.get("usage") if isinstance(ginfo.get("usage"), dict) else {}
        pt = usage.get("prompt_tokens")
        ct = usage.get("completion_tokens")
        try:
            pt = int(pt) if pt is not None else None
        except Exception:
            pt = None
        try:
            ct = int(ct) if ct is not None else None
        except Exception:
            ct = None
        template_note = ""
    else:
        system = ""
        user = ""
        completion = None
        pt = None
        ct = None
        template_note = f"template fallback ({groq_reason or 'no groq'})"
    return {
        "model": model,
        "system": system,
        "user": user,
        "completion": completion,
        "template_note": template_note,
        "prompt_tokens": pt,
        "completion_tokens": ct,
        "draft_path": draft_path,
        "groq_reason": groq_reason,
    }


def _build_inspect_record(rid, brand, raw_text, result, sig, latency_ms, passages):
    try:
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    except Exception:
        ts = datetime.datetime.utcnow().isoformat() + "+00:00"
    try:
        classify_ms = float((sig or {}).get("classify_ms")) if (sig or {}).get("classify_ms") is not None else 0.0
    except Exception:
        classify_ms = 0.0
    try:
        retrieve_ms = float((sig or {}).get("retrieve_ms")) if (sig or {}).get("retrieve_ms") is not None else 0.0
    except Exception:
        retrieve_ms = 0.0
    try:
        draft_ms = float((sig or {}).get("draft_ms")) if (sig or {}).get("draft_ms") is not None else 0.0
    except Exception:
        draft_ms = 0.0
    return {
        "request_id": rid,
        "timestamp": ts,
        "brand": brand,
        "text": (raw_text or "")[:500],
        "intent": result.intent,
        "intent_confidence": float(result.intent_confidence),
        "decision": result.decision,
        "escalate_reason": result.escalate_reason,
        "timings": {
            "classify_ms": classify_ms,
            "retrieve_ms": retrieve_ms,
            "draft_ms": draft_ms,
            "latency_ms": float(latency_ms),
        },
        "passages": passages,
        "llm": _build_llm_block(result, sig),
    }

app = FastAPI(title="Hiver Support Agent (VirginTrains primary, Apple kept)", version="2.0.0")

# ---------------------------------------------------------------------------
# Phase 4A (ADDITIVE ONLY): request-ID middleware, timing header, RFC-9457
# envelopes, slowapi 5/min/IP on /predict + /review/enqueue, OTel init,
# GET /traces tail. No existing route contract is changed.
# ---------------------------------------------------------------------------

def _rate_limit_key(request: Request):
    try:
        fwd = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
        if fwd:
            return fwd
    except Exception:
        pass
    try:
        if get_remote_address is not None:
            return get_remote_address(request)
    except Exception:
        pass
    try:
        if request.client and request.client.host:
            return request.client.host
    except Exception:
        pass
    return "unknown"


class _RequestIDMiddleware:
    """Pure-ASGI request-ID + timing middleware (no BaseHTTPMiddleware)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        rid = ""
        try:
            for k, v in scope.get("headers", []):
                try:
                    if k.decode("latin-1").lower() == "x-request-id":
                        rid = v.decode("latin-1").strip()
                        break
                except Exception:
                    continue
        except Exception:
            rid = ""
        if not rid:
            try:
                rid = uuid.uuid4().hex[:8]
            except Exception:
                rid = "unknown"
        t0 = time.perf_counter()
        try:
            hdrs = list(scope.get("headers", []) or [])
            if not any(k.decode("latin-1").lower() == "x-request-id" for k, v in hdrs):
                hdrs.append((b"x-request-id", rid.encode("latin-1")))
            scope["headers"] = hdrs
        except Exception:
            pass
        try:
            scope["request_id"] = rid
        except Exception:
            pass

        async def _send(message):
            try:
                if message.get("type") == "http.response.start":
                    h = list(message.get("headers", []) or [])
                    try:
                        h.append((b"x-request-id", rid.encode("latin-1")))
                    except Exception:
                        pass
                    try:
                        ms = (time.perf_counter() - t0) * 1000
                        h.append((b"x-process-time-ms", f"{ms:.1f}".encode("latin-1")))
                    except Exception:
                        pass
                    message["headers"] = h
            except Exception:
                pass
            await send(message)

        await self.app(scope, receive, _send)


def _problem(status: int, title: str, detail: str, request=None):
    try:
        inst = str(request.url.path) if request is not None and hasattr(request, "url") else ""
    except Exception:
        inst = ""
    return JSONResponse(
        status_code=status,
        content={"type": "about:blank", "title": title, "status": status,
                 "detail": detail, "instance": inst},
    )


async def _http_exc_handler(request: Request, exc):
    try:
        status = int(getattr(exc, "status_code", 500))
    except Exception:
        status = 500
    try:
        detail = str(getattr(exc, "detail", "error") or "error")[:500]
    except Exception:
        detail = "error"
    _titles = {400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
               404: "Not Found", 405: "Method Not Allowed", 409: "Conflict",
               422: "Unprocessable Entity", 429: "Too Many Requests",
               500: "Internal Server Error"}
    return _problem(status, _titles.get(status, "Error"), detail, request)


async def _validation_handler(request: Request, exc):
    try:
        detail = json.dumps(exc.errors())[:1000]
    except Exception:
        try:
            detail = str(exc)[:500]
        except Exception:
            detail = "validation failed"
    return _problem(422, "Unprocessable Entity", detail, request)


async def _unhandled_handler(request: Request, exc):
    try:
        logger.exception("unhandled: %s", type(exc).__name__)
    except Exception:
        pass
    return _problem(500, "Internal Server Error", "Internal Server Error", request)


def _ratelimit_429_handler(request: Request, exc):
    try:
        path = str(request.url.path)
    except Exception:
        path = ""
    try:
        detail = f"Rate limit exceeded: {exc.detail}"
    except Exception:
        detail = "Rate limit exceeded: 5 per 1 minute"
    return JSONResponse(
        status_code=429,
        content={"type": "about:blank", "title": "Too Many Requests", "status": 429,
                 "detail": detail, "instance": path},
        headers={"Retry-After": "60"},
    )


limiter = None
try:
    if _SLOWAPI_OK and Limiter is not None:
        limiter = Limiter(key_func=_rate_limit_key)
        app.state.limiter = limiter
except Exception:
    limiter = None

try:
    if StarletteHTTPException is not None:
        app.add_exception_handler(StarletteHTTPException, _http_exc_handler)
    if RequestValidationError is not None:
        app.add_exception_handler(RequestValidationError, _validation_handler)
    app.add_exception_handler(Exception, _unhandled_handler)
    if _SLOWAPI_OK and RateLimitExceeded is not None:
        app.add_exception_handler(RateLimitExceeded, _ratelimit_429_handler)
except Exception:
    pass

try:
    if _SLOWAPI_OK and SlowAPIMiddleware is not None:
        app.add_middleware(SlowAPIMiddleware)
except Exception:
    pass
try:
    app.add_middleware(_RequestIDMiddleware)
except Exception:
    pass

try:
    _rate_limit_5pm = limiter.limit("5/minute") if limiter is not None else (lambda fn: fn)
except Exception:
    def _rate_limit_5pm(fn):
        return fn

try:
    if _tracing is not None:
        _tracing.init_tracing()
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            FastAPIInstrumentor.instrument_app(app)
        except Exception:
            pass
except Exception:
    pass


@app.get("/traces")
def traces_tail(limit: int = 50):
    """Phase 4A: tail of the JSONL trace file (read-only, trivial)."""
    try:
        n = max(1, min(int(limit), 200))
    except Exception:
        n = 50
    try:
        if _tracing is None:
            return {"traces": [], "count": 0}
        path = _tracing.traces_path()
    except Exception:
        return {"traces": [], "count": 0}
    try:
        if not path.exists():
            return {"traces": [], "count": 0}
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        tail = lines[-n:] if len(lines) > n else lines
        out = []
        for ln in tail:
            try:
                out.append(json.loads(ln))
            except Exception:
                continue
        return {"traces": out, "count": len(out)}
    except Exception:
        return {"traces": [], "count": 0}

# Per-brand retriever/agent cache (brand-agnostic, keyless default).
_retrievers = {}
_agents = {}


def _normalize_brand(brand: Optional[str]) -> str:
    b = (brand or brands_mod.DEFAULT_BRAND).lower().strip()
    if b not in brands_mod.BRANDS:
        b = brands_mod.DEFAULT_BRAND
    return b


def _make_retriever_for_brand(brand: str):
    """Load per-brand TF-IDF index (data/indexes/<brand>/); fallback to legacy/apple, else None.

    Read-only: never builds or modifies KB/classifier/golden (V-EVAL owns those).
    """
    b = _normalize_brand(brand)
    try:
        for index_dir in brands_mod.get_index_candidates(b):
            try:
                p = Path(index_dir)
                vec_p = p / "tfidf_vectorizer.pkl"
                nn_p = p / "nn_index.pkl"
                ids_p = p / "doc_ids.csv"
                if not (vec_p.exists() and nn_p.exists() and ids_p.exists()):
                    continue
                import joblib
                import pandas as pd
                vec = joblib.load(vec_p)
                nn = joblib.load(nn_p)
                ids = pd.read_csv(ids_p)
                # doc_ids.csv has either tweet_id or (row,tweet_id) columns
                if "tweet_id" in ids.columns:
                    doc_ids = ids["tweet_id"].astype(str).tolist()
                else:
                    doc_ids = ids.iloc[:, -1].astype(str).tolist()
                # KB lookup per brand: data/processed/<brand>_kb.csv, fallback to apple_kb.csv
                kb_cands = []
                if b == "virgin":
                    kb_cands = [Path(r"C:\Hiver\data\processed\virgin_kb.csv")]
                else:
                    kb_cands = [Path(r"C:\Hiver\data\processed\apple_kb.csv")]
                lookup: dict = {}
                for kb_path in kb_cands:
                    try:
                        if kb_path.exists():
                            kb = pd.read_csv(kb_path, usecols=["tweet_id", "text", "clean"])
                            lookup = {str(r.tweet_id): (r.text, r.clean) for r in kb.itertuples()}
                            break
                    except Exception:
                        continue

                class _BrandRetriever:
                    def __init__(self, _vec, _nn, _doc_ids, _lookup):
                        self.vec = _vec
                        self.nn = _nn
                        self.doc_ids = _doc_ids
                        self.lookup = _lookup

                    def query(self, text: str, k: int = 5):
                        Xq = self.vec.transform([(text or "").lower()])
                        dist, idx = self.nn.kneighbors(Xq, n_neighbors=min(k, len(self.doc_ids)))
                        out = []
                        for d, j in zip(dist[0], idx[0]):
                            tid = self.doc_ids[j]
                            raw, clean = self.lookup.get(tid, ("", ""))
                            out.append({"tweet_id": tid, "distance": float(d),
                                        "score": float(1 - d), "text": raw, "clean": clean})
                        return out

                return _BrandRetriever(vec, nn, doc_ids, lookup)
            except Exception:
                continue
    except Exception:
        pass
    # Final fallback: legacy apple Retriever for apple only, else None
    if b == "apple":
        try:
            return Retriever()
        except Exception:
            return None
    return None


def get_agent(brand: Optional[str] = None):
    b = _normalize_brand(brand)
    if b not in _agents or _agents[b] is None:
        try:
            if b not in _retrievers:
                _retrievers[b] = _make_retriever_for_brand(b)
        except Exception:
            _retrievers[b] = None
        try:
            _agents[b] = AppleAgent(_retrievers.get(b), brand=b)
        except Exception:
            # Last resort: agent without retrieval (fail-closed, still escalates correctly)
            _agents[b] = AppleAgent(None, brand=b)
    return _agents[b]


# Backward-compat single-agent accessor (defaults to virgin primary).
def get_default_agent():
    return get_agent(brands_mod.DEFAULT_BRAND)

class PredictIn(BaseModel):
    text: str
    brand: Optional[str] = Field(default="virgin", description="Brand: virgin (default, primary) or apple (v1 evidence). Unknown falls back to virgin.")


class JudgeIn(BaseModel):
    intent: str = "other_out_of_scope"
    draft_reply: str = ""
    passage_ids: list = []
    inbound: str = ""


@app.get("/passages")
def passages(brand: Optional[str] = "virgin", q: str = ""):
    """Live retrieval evidence for the frontend 3D graph + ranked list."""
    b = _normalize_brand(brand)
    agent = get_agent(b)
    try:
        res = agent.retriever.query((q or "")[:500], k=5) if agent.retriever else []
    except Exception:
        res = []
    return [{"tweet_id": p.get("tweet_id", ""), "score": round(float(p.get("score", 0.0)), 3),
             "text": (p.get("text") or "")[:200]} for p in res]


@app.post("/judge")
def judge(inp: JudgeIn):
    """Live heuristic judge (advisory). LLM hook stays gated (needs key + kappa study)."""
    draft = inp.draft_reply or ""
    low = draft.lower()
    ground = 1 + (1 if inp.passage_ids else 0) + (1 if any(k in low for k in ["settings", "restart", "check", "try", "dm us"]) else 0) + (1 if len(draft.split()) >= 12 else 0)
    ground = max(1, min(5, ground + 1))
    unsafe = any(k in low for k in ["password:", "ssn"])
    safety = 2 if unsafe else 5
    verdict = "FAIL" if (ground <= 2 or safety <= 2) else "PASS"
    return {"groundedness": ground, "safety": safety, "verdict": verdict, "rubric": "judge-v1-heuristic"}

@app.get("/healthz")
def healthz():
    return {"ok": True}


# ---- Graphify repository knowledge graph (offline-built artifact, no LLM at serve time)
_GRAPHIFY_DIR = Path(__file__).resolve().parent.parent / "graphify-out"


@app.get("/graph")
def graph_page():
    """Interactive repository knowledge graph (graphify-out/graph.html)."""
    fp = _GRAPHIFY_DIR / "graph.html"
    if not fp.exists():
        return JSONResponse({"detail": "graph artifact not built (see scripts/build_docs_overlay.py)"}, status_code=404)
    return FileResponse(str(fp), media_type="text/html")


@app.get("/graph/json")
def graph_json():
    """Raw knowledge-graph JSON (nodes/edges) for the repo map."""
    fp = _GRAPHIFY_DIR / "graph.json"
    if not fp.exists():
        return JSONResponse({"detail": "graph artifact not built (see scripts/build_docs_overlay.py)"}, status_code=404)
    return FileResponse(str(fp), media_type="application/json")

@app.get("/readyz")
def readyz():
    try:
        # Both brands must be loadable (apple kept as transfer proof).
        get_agent("virgin")
        get_agent("apple")
        return {"ready": True}
    except Exception as e:
        return JSONResponse({"ready": False, "error": str(e)}, status_code=500)

@app.post("/predict")
@_rate_limit_5pm
def predict(inp: PredictIn, request: Request):
    t0 = time.perf_counter()
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    raw = inp.text or ""
    truncated = len(raw) > MAX_CHARS
    text = raw[:MAX_CHARS] if truncated else raw
    brand = _normalize_brand(inp.brand)
    agent = get_agent(brand)
    r = agent.handle(text, brand)
    # Phase 4A: OTel pipeline spans + structlog bound log (fail-closed).
    try:
        if _tracing is not None:
            _tracing.emit_pipeline_spans(rid, brand, r.intent, r.escalate_signals or {},
                                         model="openai/gpt-oss-20b")
    except Exception:
        pass
    try:
        if _tracing is not None:
            _tracing.get_logger(rid).info("predict", brand=brand, intent=r.intent,
                                          decision=r.decision)
    except Exception:
        pass
    latency_ms = round((time.perf_counter() - t0) * 1000, 1)
    _record_latency(brand, latency_ms, r.decision)
    log_line = json.dumps({"request_id": rid, "brand": brand, "intent": r.intent,
                           "decision": r.decision, "latency_ms": latency_ms,
                           "truncated": truncated,
                           "draft_path": r.escalate_signals.get("draft_path", "template")})
    print(log_line, flush=True)
    logger.info(log_line)
    sig = r.escalate_signals or {}
    groq_reason = sig.get("groq_reason", "") if isinstance(sig, dict) else ""
    try:
        _store_inspect(_build_inspect_record(
            rid, brand, raw, r, sig, latency_ms, _collect_passages(agent, text, k=5)))
    except Exception:
        pass
    return {
        "request_id": rid,
        "brand": brand,
        "intent": r.intent,
        "intent_confidence": r.intent_confidence,
        "draft_reply": r.draft_reply,
        "grounding_passage_ids": r.grounding_passage_ids,
        "decision": r.decision,
        "escalate_reason": r.escalate_reason,
        "signals": r.escalate_signals,
        "draft_path": sig.get("draft_path", "template") if isinstance(sig, dict) else "template",
        "groq_reason": groq_reason,
        "latency_ms": latency_ms,
        "truncated": truncated,
    }

@app.post("/predict/stream")
def predict_stream(inp: PredictIn, request: Request):
    """SSE: stage events (classify/retrieve) live, then Groq draft chunks live, then final technicals."""
    raw = inp.text or ""
    truncated = len(raw) > MAX_CHARS
    text = raw[:MAX_CHARS] if truncated else raw
    brand = _normalize_brand(inp.brand)
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    t0 = time.perf_counter()

    def gen():
        yield f"data: {json.dumps({'event': 'start', 'request_id': rid, 'brand': brand})}\n\n"
        agent = get_agent(brand)
        # Fast deterministic stages (same code path as /predict, timed live)
        r = agent.handle(text, brand)
        try:
            if _tracing is not None:
                _tracing.emit_pipeline_spans(rid, brand, r.intent, r.escalate_signals or {},
                                             model="openai/gpt-oss-20b")
        except Exception:
            pass
        yield f"data: {json.dumps({'event': 'stages', 'intent': r.intent, 'intent_confidence': r.intent_confidence, 'classify_ms': (r.escalate_signals or {}).get('classify_ms'), 'retrieve_ms': (r.escalate_signals or {}).get('retrieve_ms'), 'draft_ms': (r.escalate_signals or {}).get('draft_ms'), 'latency_ms': r.latency_ms})}\n\n"
        sig = r.escalate_signals or {}
        if sig.get("draft_path") == "groq":
            # Non-stream path already produced a Groq draft; replay it as one chunk (live timings preserved)
            yield f"data: {json.dumps({'event': 'token', 'text': r.draft_reply})}\n\n"
        else:
            # Try live Groq streaming so judges SEE tokens arrive; fail-closed to template
            try:
                from src import groq_draft as groq_mod
                passages = []
                try:
                    passages = agent.retriever.query(text, k=3) if agent.retriever else []
                except Exception:
                    passages = []
                streamed_any = False
                for piece, done in groq_mod.stream_groq_draft(r.intent, text, passages, brand):
                    if piece:
                        streamed_any = True
                        yield f"data: {json.dumps({'event': 'token', 'text': piece})}\n\n"
                    if done is not None and isinstance(done, dict) and done.get("draft"):
                        r.draft_reply = done["draft"]
                        sig["draft_path"] = "groq"
                if not streamed_any:
                    yield f"data: {json.dumps({'event': 'token', 'text': r.draft_reply})}\n\n"
            except Exception:
                yield f"data: {json.dumps({'event': 'token', 'text': r.draft_reply})}\n\n"
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        _record_latency(brand, latency_ms, r.decision)
        try:
            _store_inspect(_build_inspect_record(
                rid, brand, raw, r, (r.escalate_signals or {}), latency_ms,
                _collect_passages(agent, text, k=5)))
        except Exception:
            pass
        try:
            log_line = json.dumps({"request_id": rid, "brand": brand, "intent": r.intent,
                                   "decision": r.decision, "latency_ms": latency_ms,
                                   "truncated": truncated,
                                   "draft_path": (r.escalate_signals or {}).get("draft_path", "template")})
            print(log_line, flush=True)
            logger.info(log_line)
        except Exception:
            pass
        final = {"event": "final", "request_id": rid, "brand": brand, "intent": r.intent,
                 "intent_confidence": r.intent_confidence, "draft_reply": r.draft_reply,
                 "grounding_passage_ids": r.grounding_passage_ids, "decision": r.decision,
                 "escalate_reason": r.escalate_reason, "signals": r.escalate_signals,
                 "draft_path": (r.escalate_signals or {}).get("draft_path", "template"),
                 "latency_ms": latency_ms, "truncated": truncated}
        yield f"data: {json.dumps(final)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


class EvalRunIn(BaseModel):
    n: Optional[int] = 20
    seed: Optional[int] = 11
    brand: Optional[str] = "virgin"


@app.get("/inspect/{request_id}")
def inspect_one(request_id: str):
    rec = _get_inspect(request_id)
    if rec is None:
        return JSONResponse({"detail": "unknown request"}, status_code=404)
    # Resolve missing passage texts via the brand retriever at read time.
    try:
        passages = rec.get("passages") or []
        if any(not ((p or {}).get("text") or "").strip() for p in passages):
            brand = rec.get("brand") or brands_mod.DEFAULT_BRAND
            try:
                agent = get_agent(brand)
                retr = getattr(agent, "retriever", None)
                fresh_by_id = {}
                try:
                    if retr is not None:
                        fresh_res = retr.query(rec.get("text") or "", k=5)
                        fresh_by_id = {str(p.get("tweet_id")): p for p in (fresh_res or [])}
                except Exception:
                    fresh_by_id = {}
                try:
                    lookup = getattr(retr, "lookup", {}) or {}
                except Exception:
                    lookup = {}
                for p in passages:
                    try:
                        if not (p.get("text") or "").strip():
                            tid = str(p.get("tweet_id", ""))
                            if tid in fresh_by_id and (fresh_by_id[tid].get("text") or "").strip():
                                p["text"] = (fresh_by_id[tid].get("text") or "")[:200]
                            elif tid in lookup:
                                v = lookup[tid]
                                if isinstance(v, (list, tuple)) and len(v) > 0:
                                    p["text"] = (v[0] or "")[:200]
                                elif isinstance(v, str):
                                    p["text"] = v[:200]
                    except Exception:
                        continue
            except Exception:
                pass
    except Exception:
        pass
    return rec


@app.get("/logs/stream")
def logs_stream():
    def gen():
        # Snapshot backlog + sequence atomically so lines arriving mid-replay are not lost.
        try:
            with _log_lock:
                backlog = list(_log_tail)
                last_seq = _log_seq
        except Exception:
            backlog, last_seq = [], 0
        for line in backlog:
            yield f"data: {line}\n\n"
        last_beat = time.time()
        while True:
            time.sleep(0.5)
            try:
                with _log_lock:
                    seq = _log_seq
                    if seq > last_seq:
                        cur = list(_log_tail)
                        new_count = min(seq - last_seq, len(cur))
                        new_lines = cur[len(cur) - new_count:] if new_count else []
                        last_seq = seq
                    else:
                        new_lines = []
            except Exception:
                new_lines = []
            try:
                for line in new_lines:
                    yield f"data: {line}\n\n"
                now = time.time()
                if now - last_beat >= 15:
                    yield ":\n\n"
                    last_beat = now
            except GeneratorExit:
                break
            except Exception:
                continue
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/eval/run")
def eval_run(inp: EvalRunIn):
    try:
        n = int(inp.n) if inp.n is not None else 20
    except Exception:
        n = 20
    n = max(1, min(n, 50))
    try:
        seed = int(inp.seed) if inp.seed is not None else 11
    except Exception:
        seed = 11
    brand = _normalize_brand(inp.brand if inp.brand else brands_mod.DEFAULT_BRAND)

    def gen():
        try:
            import pandas as pd
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'detail': f'pandas unavailable: {e}'[:200]})}\n\n"
            yield "data: [DONE]\n\n"
            return
        try:
            from src.agent import _predict_for_brand, draft_grounded, decide_escalation
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'detail': f'agent import failed: {e}'[:200]})}\n\n"
            yield "data: [DONE]\n\n"
            return
        csv_path = Path(__file__).resolve().parent.parent / "evaluation" / "virgin" / "golden_human_200.csv"
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'detail': str(e)[:200]})}\n\n"
            yield "data: [DONE]\n\n"
            return
        try:
            n_eff = min(n, len(df))
            sample = df.sample(n=n_eff, random_state=seed).reset_index(drop=True)
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'detail': str(e)[:200]})}\n\n"
            yield "data: [DONE]\n\n"
            return
        try:
            proto = get_agent(brand)
            retr = getattr(proto, "retriever", None)
        except Exception:
            retr = None
        total = len(sample)
        intent_ok = 0
        esc_ok_cnt = 0
        for idx, row in enumerate(sample.itertuples()):
            try:
                text = getattr(row, "text", "") or ""
                human_intent = str(getattr(row, "human_intent", "") or "")
                try:
                    human_esc = int(getattr(row, "human_escalate", 0))
                except Exception:
                    human_esc = 0
                try:
                    pred, conf = _predict_for_brand(brand, text)
                except Exception:
                    pred, conf = "other_out_of_scope", 0.35
                try:
                    passages = retr.query(text, k=5) if retr is not None else []
                except Exception:
                    passages = []
                try:
                    _draft, _ids, _unsup = draft_grounded(pred, passages, brand)
                except Exception:
                    pass
                try:
                    decision, _reason, _signals = decide_escalation(pred, float(conf), text, passages, brand)
                except Exception:
                    decision = "escalate"
                pred_esc = 1 if decision == "escalate" else 0
                ok = bool(str(pred) == human_intent)
                esc_ok = bool(pred_esc == human_esc)
                if ok:
                    intent_ok += 1
                if esc_ok:
                    esc_ok_cnt += 1
                item = {"event": "item", "i": idx, "n": total,
                        "text": (text or "")[:120],
                        "human_intent": human_intent, "pred_intent": str(pred), "ok": ok,
                        "human_esc": int(human_esc), "pred_esc": int(pred_esc), "esc_ok": esc_ok}
                yield f"data: {json.dumps(item)}\n\n"
            except Exception:
                continue
        intent_acc = round(intent_ok / total, 4) if total else 0.0
        esc_acc = round(esc_ok_cnt / total, 4) if total else 0.0
        yield f"data: {json.dumps({'event': 'done', 'n': total, 'intent_acc': intent_acc, 'esc_acc': esc_acc})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/embed2d")
def embed2d(brand: Optional[str] = "virgin", q: str = ""):
    b = _normalize_brand(brand)
    query_text = (q or "")[:500]
    try:
        agent = get_agent(b)
        retr = getattr(agent, "retriever", None)
        if retr is None or getattr(retr, "vec", None) is None:
            return {"points": [], "query": {"x": 0.0, "y": 0.0}}
        try:
            passages = retr.query(query_text, k=5)
        except Exception:
            passages = []
        if not passages:
            return {"points": [], "query": {"x": 0.0, "y": 0.0}}
        corpus = [(query_text or "").lower()]
        for p in passages[:5]:
            try:
                c = (p.get("clean") or p.get("text") or "")
                corpus.append((c or "").lower())
            except Exception:
                corpus.append("")
        try:
            X = retr.vec.transform(corpus)
        except Exception:
            return {"points": [], "query": {"x": 0.0, "y": 0.0}}
        try:
            from sklearn.decomposition import TruncatedSVD
            import numpy as np
            svd = TruncatedSVD(n_components=2, random_state=7)
            coords = np.asarray(svd.fit_transform(X), dtype=float)
            normed = np.zeros_like(coords)
            for ax in range(2):
                col = coords[:, ax]
                mn = float(col.min())
                mx = float(col.max())
                if mx > mn:
                    normed[:, ax] = 2 * (col - mn) / (mx - mn) - 1
                else:
                    normed[:, ax] = 0.0
            normed = np.round(normed, 4)
            qx, qy = float(normed[0, 0]), float(normed[0, 1])
            points = []
            for i, p in enumerate(passages[:5]):
                try:
                    points.append({
                        "tweet_id": str(p.get("tweet_id", "")),
                        "x": float(normed[i + 1, 0]),
                        "y": float(normed[i + 1, 1]),
                        "score": round(float(p.get("score", 0.0)), 4),
                    })
                except Exception:
                    continue
            return {"points": points, "query": {"x": qx, "y": qy}}
        except Exception:
            return {"points": [], "query": {"x": 0.0, "y": 0.0}}
    except Exception:
        return {"points": [], "query": {"x": 0.0, "y": 0.0}}


def _pct(sorted_vals, q):
    if not sorted_vals:
        return 0.0
    i = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return round(float(sorted_vals[i]), 1)


def _brand_summary(b: str):
    c = _metrics_per_brand.get(b, _fresh_counters())
    n = c["predict_count"]
    tot = c["total_latency_ms"]
    avg = round(tot / n, 1) if n else 0.0
    s = sorted(c.get("latencies", []))
    return {"predict_count": n, "escalate_count": c["escalate_count"],
            "auto_count": c["auto_count"], "avg_latency_ms": avg,
            "p50_latency_ms": _pct(s, 0.50), "p95_latency_ms": _pct(s, 0.95),
            "total_latency_ms": round(tot, 1)}

SERVER_STARTED_AT = datetime.datetime.now(datetime.timezone.utc).isoformat()

# ---------------------------------------------------------------------------
# Phase 3 (HITL review queue) — ADDITIVE ONLY. No existing route above is
# modified. All state lives in data/processed/review_queue.db via
# src/review_store.py (SQLite, gitignored runtime state).
# ---------------------------------------------------------------------------

class ReviewEnqueueIn(BaseModel):
    text: str = ""
    brand: Optional[str] = "virgin"
    idempotency_key: Optional[str] = None
    sla_minutes: Optional[int] = None


class ReviewApproveIn(BaseModel):
    reviewer: Optional[str] = "reviewer"
    rationale: Optional[str] = ""


class ReviewEditIn(BaseModel):
    reviewer: Optional[str] = "reviewer"
    rationale: Optional[str] = ""
    final_text: Optional[str] = ""
    corrected_intent: Optional[str] = None


class ReviewRejectIn(BaseModel):
    reviewer: Optional[str] = "reviewer"
    rationale: Optional[str] = ""


def _review_store():
    from src import review_store as _rs
    return _rs


@app.get("/review/queue")
def review_queue(status: Optional[str] = None, brand: Optional[str] = None,
                 limit: Optional[int] = 100, offset: Optional[int] = 0):
    rs = _review_store()
    try:
        lim = max(1, min(int(limit or 100), 500))
    except Exception:
        lim = 100
    try:
        off = max(0, int(offset or 0))
    except Exception:
        off = 0
    st = (status or "").upper().strip() or None
    if st and st not in ("PENDING", "APPROVED", "APPROVED_WITH_EDITS", "REJECTED", "EXPIRED"):
        return JSONResponse({"detail": f"unknown status {status}"}, status_code=400)
    try:
        rs.expire_overdue()
    except Exception:
        pass
    items = rs.list_queue(status=st, brand=(_normalize_brand(brand) if brand else None),
                          limit=lim, offset=off)
    return {"items": items, "count": len(items)}


@app.get("/review/stats")
def review_stats():
    rs = _review_store()
    try:
        rs.expire_overdue()
    except Exception:
        pass
    return rs.stats()


@app.get("/review/matrix")
def review_matrix():
    rs = _review_store()
    matrix = rs.load_matrix()
    # Coverage-vs-risk grid for the frontend threshold slider (read-only ref).
    grid = None
    try:
        tp = Path(__file__).resolve().parent.parent / "evaluation" / "virgin" / "thresholds.json"
        if tp.exists():
            grid = json.loads(tp.read_text(encoding="utf-8")).get("msp_floor", {}).get("grid")
    except Exception:
        grid = None
    return {"matrix": matrix, "coverage_grid": grid}


@app.post("/review/expire-sweep")
def review_expire_sweep():
    rs = _review_store()
    try:
        n = int(rs.expire_overdue())
    except Exception as e:
        return JSONResponse({"detail": str(e)[:200]}, status_code=500)
    return {"expired": n}


@app.post("/review/enqueue")
@_rate_limit_5pm
def review_enqueue(inp: ReviewEnqueueIn, request: Request):
    rs = _review_store()
    brand = _normalize_brand(inp.brand)
    text = (inp.text or "")[:MAX_CHARS]
    if not text.strip():
        return JSONResponse({"detail": "empty text"}, status_code=400)
    agent = get_agent(brand)
    r = agent.handle(text, brand)
    # Phase 4A: trace the enqueue path too (fail-closed).
    try:
        if _tracing is not None:
            _rid = ""
            try:
                _rid = request.headers.get("X-Request-ID", "") or ""
            except Exception:
                _rid = ""
            _tracing.emit_pipeline_spans(_rid or "review-enqueue", brand, r.intent,
                                         r.escalate_signals or {}, model="openai/gpt-oss-20b")
    except Exception:
        pass
    # Matrix route is advisory; the queue holds agent escalations.
    try:
        route = rs.route_for(r.intent, float(r.intent_confidence))
    except Exception:
        route = "review"
    if r.decision != "escalate":
        return {"enqueued": False, "decision": r.decision,
                "intent": r.intent, "intent_confidence": r.intent_confidence,
                "escalate_reason": r.escalate_reason, "route": route,
                "brand": brand}
    try:
        row = rs.enqueue_from_result(r, text, brand,
                                     idempotency_key=(inp.idempotency_key or None),
                                     sla_minutes=inp.sla_minutes)
    except Exception as e:
        return JSONResponse({"detail": str(e)[:200]}, status_code=500)
    row["route"] = route
    return row


@app.get("/review/{escalation_id}")
def review_get(escalation_id: str):
    rs = _review_store()
    row = rs.get_escalation(escalation_id)
    if not row:
        return JSONResponse({"detail": "unknown escalation"}, status_code=404)
    return row


@app.get("/review/{escalation_id}/transfer")
def review_transfer(escalation_id: str):
    rs = _review_store()
    row = rs.get_escalation(escalation_id)
    if not row:
        return JSONResponse({"detail": "unknown escalation"}, status_code=404)
    return rs.build_warm_transfer(row)


@app.get("/review/{escalation_id}/audit")
def review_audit(escalation_id: str):
    rs = _review_store()
    if not rs.get_escalation(escalation_id):
        return JSONResponse({"detail": "unknown escalation"}, status_code=404)
    return {"escalation_id": escalation_id, "events": rs.list_audit(escalation_id)}


def _do_review_transition(escalation_id: str, to_status: str, reviewer, rationale,
                          final_text=None, corrected_intent=None):
    rs = _review_store()
    try:
        return rs.transition(escalation_id, to_status, reviewer=reviewer or "reviewer",
                             rationale=rationale or "", final_text=final_text,
                             corrected_intent=corrected_intent)
    except KeyError:
        return JSONResponse({"detail": "unknown escalation"}, status_code=404)
    except ValueError as e:
        return JSONResponse({"detail": str(e)[:200]}, status_code=409)


@app.post("/review/{escalation_id}/approve")
def review_approve(escalation_id: str, inp: ReviewApproveIn):
    return _do_review_transition(escalation_id, "APPROVED", inp.reviewer, inp.rationale)


@app.post("/review/{escalation_id}/edit")
def review_edit(escalation_id: str, inp: ReviewEditIn):
    return _do_review_transition(escalation_id, "APPROVED_WITH_EDITS", inp.reviewer,
                                 inp.rationale, final_text=inp.final_text,
                                 corrected_intent=inp.corrected_intent)


@app.post("/review/{escalation_id}/reject")
def review_reject(escalation_id: str, inp: ReviewRejectIn):
    return _do_review_transition(escalation_id, "REJECTED", inp.reviewer, inp.rationale)

@app.get("/metrics")
def metrics():
    with _metrics_lock:
        per = {b: _brand_summary(b) for b in sorted(set(list(_metrics_per_brand.keys()) + brands_mod.list_brands()))}
        tot_n = sum(v["predict_count"] for v in per.values())
        tot_esc = sum(v["escalate_count"] for v in per.values())
        tot_auto = sum(v["auto_count"] for v in per.values())
        tot_lat = round(sum(v["total_latency_ms"] for v in per.values()), 1)
    avg = round(tot_lat / tot_n, 1) if tot_n else 0.0
    # Backward-compat top-level totals + per-brand breakdown.
    return {"predict_count": tot_n, "escalate_count": tot_esc, "auto_count": tot_auto,
            "avg_latency_ms": avg, "total_latency_ms": tot_lat,
            "started_at": SERVER_STARTED_AT,
            "per_brand": per}
