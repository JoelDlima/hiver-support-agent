"""FastAPI for Hiver support agent (VirginTrains primary, AppleSupport kept). Stateless, CPU-only + optional Groq."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import json
import logging
import threading
import time, uuid
from pathlib import Path
from src.agent import AppleAgent
from src.retriever import Retriever
from src import brands as brands_mod

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

app = FastAPI(title="Hiver Support Agent (VirginTrains primary, Apple kept)", version="2.0.0")

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
def predict(inp: PredictIn, request: Request):
    t0 = time.perf_counter()
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    raw = inp.text or ""
    truncated = len(raw) > MAX_CHARS
    text = raw[:MAX_CHARS] if truncated else raw
    brand = _normalize_brand(inp.brand)
    agent = get_agent(brand)
    r = agent.handle(text, brand)
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
            "per_brand": per}
