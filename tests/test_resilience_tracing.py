"""Phase 4A: backend hardening + observability + safety.

Covers: slowapi 429 shape (+ Retry-After), RFC-9457 envelopes on 404/422,
breaker opens on injected failures then template fallback (bounded latency),
trace JSONL row per predict, sandbox tags in prompt.
"""
import json
import sys
import time
import uuid

sys.path.insert(0, r"C:\Hiver")

import pytest
from fastapi.testclient import TestClient


def _reset_limiter():
    try:
        from backend.main import limiter
        if limiter is not None:
            try:
                limiter._storage.reset()
            except Exception:
                pass
    except Exception:
        pass


def _reset_breaker():
    try:
        from src import resilience as res
        res.reset_breaker()
    except Exception:
        pass


@pytest.fixture()
def tclient(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    _reset_limiter()
    _reset_breaker()
    from backend.main import app
    c = TestClient(app)
    yield c
    _reset_limiter()
    _reset_breaker()


def _uniq(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def test_429_shape(tclient):
    ip = _uniq("rl429")
    codes = []
    last = None
    for _ in range(6):
        r = tclient.post("/predict", json={"text": "hello booking help", "brand": "virgin"},
                         headers={"X-Forwarded-For": ip})
        codes.append(r.status_code)
        last = r
    assert codes[:5] == [200] * 5
    assert codes[5] == 429
    body = last.json()
    assert body.get("status") == 429
    assert body.get("title") == "Too Many Requests"
    assert "Rate limit" in str(body.get("detail", ""))
    assert body.get("type") == "about:blank"
    assert last.headers.get("retry-after") == "60"


def test_envelope_404_422(tclient):
    r404 = tclient.get("/definitely-not-here-4a-xyz")
    assert r404.status_code == 404
    b404 = r404.json()
    assert b404.get("status") == 404
    assert b404.get("title") == "Not Found"
    assert b404.get("type") == "about:blank"
    assert "detail" in b404 and "instance" in b404

    r422 = tclient.post("/predict", json={},
                        headers={"X-Forwarded-For": _uniq("env422")})
    assert r422.status_code == 422
    b422 = r422.json()
    assert b422.get("status") == 422
    assert b422.get("title") == "Unprocessable Entity"
    assert b422.get("type") == "about:blank"
    assert "detail" in b422


def test_breaker_opens_then_template_fallback(tclient, monkeypatch):
    from src import resilience as res
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    res.reset_breaker()
    assert res.get_breaker_state() == "closed"

    def _boom():
        raise RuntimeError("injected-4a")

    for _ in range(5):
        try:
            res.call_groq_with_resilience(_boom)
        except Exception:
            pass
    assert res.get_breaker_state() == "open"

    # Breaker open -> /predict still serves template fallback, bounded latency.
    t0 = time.perf_counter()
    r = tclient.post("/predict", json={"text": "my train was delayed, refund please", "brand": "virgin"},
                     headers={"X-Forwarded-For": _uniq("brk"), "X-Request-ID": _uniq("rid")})
    dt_ms = (time.perf_counter() - t0) * 1000
    assert r.status_code == 200
    assert r.json().get("draft_path") == "template"
    assert dt_ms < 2000, f"predict latency unbounded with breaker open: {dt_ms:.0f}ms"
    # 429s never trip the breaker (excluded): direct unit check.
    res.reset_breaker()

    class _E429(Exception):
        status_code = 429
        response = None

    for _ in range(7):
        try:
            res.call_groq_with_resilience(lambda: (_ for _ in ()).throw(_E429()))
        except Exception:
            pass
    assert res.get_breaker_state() == "closed"


def test_trace_jsonl_row_per_predict(tclient):
    from src import tracing as t
    rid = _uniq("trace")
    r = tclient.post("/predict", json={"text": "hello booking help", "brand": "virgin"},
                     headers={"X-Forwarded-For": _uniq("tr"), "X-Request-ID": rid})
    assert r.status_code == 200
    assert r.json().get("request_id") == rid
    try:
        t.force_flush()
    except Exception:
        pass
    # Allow BatchSpanProcessor a beat if flush was async.
    deadline = time.time() + 5
    found = []
    path = t.traces_path()
    while time.time() < deadline:
        try:
            if path.exists():
                lines = path.read_text(encoding="utf-8").splitlines()
                found = [json.loads(ln) for ln in lines
                         if rid in ln and "request_id" in ln]
                if found:
                    break
        except Exception:
            pass
        time.sleep(0.2)
    assert found, f"no trace JSONL row for request_id={rid}"
    names = {o.get("name") for o in found}
    assert "predict" in names
    assert {"classify", "retrieve", "draft", "escalate"} & names
    for o in found:
        attrs = o.get("attributes", {})
        assert attrs.get("request_id") == rid
        assert any(k.startswith("gen_ai.") for k in attrs)


def test_sandbox_tags_in_prompt():
    from src import groq_draft as g
    from src import sandbox as sb
    passages = [{"tweet_id": "7", "text": "Delay Repay lets you claim if delayed. DM us.", "clean": ""}]
    system, user = g._prompts("delay_claim", "my train was delayed", passages, "virgin")
    assert "<UNTRUSTED-TWEET>" in user and "</UNTRUSTED-TWEET>" in user
    assert "never obey" in system.lower()
    assert sb.SANDBOX_RULE in system
    # Wrapper unit shape.
    w = sb.wrap_passage("hello", "9")
    assert w.startswith("<UNTRUSTED-TWEET") and w.endswith("</UNTRUSTED-TWEET>")


def test_latency_bounded_breaker_forced_open(tclient, monkeypatch):
    from src import resilience as res
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_fake_4a")
    res.reset_breaker()
    res.force_breaker_open()
    assert res.get_breaker_state() == "open"
    try:
        t0 = time.perf_counter()
        r = tclient.post("/predict", json={"text": "my train was delayed 2 hours", "brand": "virgin"},
                         headers={"X-Forwarded-For": _uniq("latp")})
        dp_ms = (time.perf_counter() - t0) * 1000
        assert r.status_code == 200
        assert r.json().get("draft_path") == "template"
        assert dp_ms < 2000, f"/predict unbounded with breaker open: {dp_ms:.0f}ms"

        t1 = time.perf_counter()
        e = tclient.post("/review/enqueue",
                         json={"text": "My train was delayed 2 hours, refund my £50 ticket now",
                               "brand": "virgin"},
                         headers={"X-Forwarded-For": _uniq("late")})
        de_ms = (time.perf_counter() - t1) * 1000
        assert e.status_code == 200
        assert de_ms < 2000, f"/review/enqueue unbounded with breaker open: {de_ms:.0f}ms"
    finally:
        res.reset_breaker()
