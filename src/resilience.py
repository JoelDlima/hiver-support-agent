"""Phase 4A: shared httpx client + tenacity retry (429/5xx-only) + pybreaker.

- Shared httpx AsyncClient with granular timeouts (connect/read/write/pool).
- Tenacity retry: 429/5xx ONLY, max 3 attempts total, exponential jitter,
  honoring Retry-After when present on the exception response.
- pybreaker: fail_max=5, reset_timeout=30s, EXCLUDING 429 (rate limits are
  backpressure, not system failure).
- call_groq_with_resilience(fn, ...): Groq-call wrapper used by the groq path
  (fail-closed to template on CircuitBreakerError by the caller).
"""

import threading
import time

import httpx
import pybreaker
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

# Granular timeouts: fail fast on connect, tolerate model read latency.
GRANULAR_TIMEOUT = httpx.Timeout(connect=3.0, read=10.0, write=5.0, pool=3.0)
HTTP_LIMITS = httpx.Limits(max_connections=50, max_keepalive_connections=20)

_client = None
_client_lock = threading.Lock()


def get_http_client():
    """Shared httpx AsyncClient singleton (granular timeouts)."""
    global _client
    with _client_lock:
        if _client is None:
            try:
                _client = httpx.AsyncClient(timeout=GRANULAR_TIMEOUT, limits=HTTP_LIMITS)
            except Exception:
                _client = httpx.AsyncClient(timeout=10.0)
        return _client


def _status_of(exc):
    """Extract HTTP status int from SDK/httpx exceptions, else None."""
    try:
        v = getattr(exc, "status_code", None)
        if isinstance(v, int) and 100 <= v <= 599:
            return v
        try:
            if v is not None:
                iv = int(v)
                if 100 <= iv <= 599:
                    return iv
        except Exception:
            pass
    except Exception:
        pass
    try:
        resp = getattr(exc, "response", None)
        if resp is not None:
            v = getattr(resp, "status_code", None)
            if isinstance(v, int) and 100 <= v <= 599:
                return v
            try:
                if v is not None:
                    iv = int(v)
                    if 100 <= iv <= 599:
                        return iv
            except Exception:
                pass
    except Exception:
        pass
    return None


def _is_429(exc):
    try:
        return _status_of(exc) == 429
    except Exception:
        return False


def _is_retryable(exc):
    """Retry ONLY on 429 / 5xx (never on 4xx, validation, or local errors)."""
    try:
        s = _status_of(exc)
        if s is None:
            return False
        if s == 429:
            return True
        return 500 <= s <= 599
    except Exception:
        return False


def _retry_after_seconds(exc):
    """Honor Retry-After / retry-after response header if present (capped)."""
    try:
        resp = getattr(exc, "response", None)
        headers = None
        if resp is not None:
            headers = getattr(resp, "headers", None)
        if not headers:
            headers = getattr(exc, "headers", None)
        if not headers:
            return None
        try:
            get = headers.get if hasattr(headers, "get") else None
            val = None
            if get:
                val = get("retry-after", None)
                if val is None:
                    val = get("Retry-After", None)
            if val is None:
                return None
            secs = float(str(val).strip().split(",")[0])
            if secs < 0:
                return None
            return min(secs, 10.0)
        except Exception:
            return None
    except Exception:
        return None


def _resilience_wait(retry_state):
    """Exponential jitter base, maxed with Retry-After when present."""
    try:
        base = wait_exponential_jitter(initial=0.5, max=4.0)(retry_state)
    except Exception:
        base = 0.5
    try:
        exc = None
        if getattr(retry_state, "outcome", None) is not None:
            try:
                exc = retry_state.outcome.exception()
            except Exception:
                exc = None
        if exc is not None:
            ra = _retry_after_seconds(exc)
            if ra is not None:
                try:
                    return max(float(base), float(ra))
                except Exception:
                    return ra
    except Exception:
        pass
    return base


def retry_groq(fn):
    """Tenacity decorator: 429/5xx-only, <=3 attempts, jitter + Retry-After."""
    return retry(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(3),
        wait=_resilience_wait,
        reraise=True,
    )(fn)


def call_with_retry(fn, *args, **kwargs):
    """Call fn with the groq retry policy (reraise after <=3 attempts)."""
    return retry_groq(fn)(*args, **kwargs)


def _exclude_429(exc):
    """pybreaker exclusion: 429 is backpressure, not a system failure."""
    try:
        return _is_429(exc)
    except Exception:
        return False


groq_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    exclude=[_exclude_429],
)


def is_breaker_open():
    try:
        return groq_breaker.current_state == pybreaker.STATE_OPEN
    except Exception:
        return False


def get_breaker_state():
    try:
        return groq_breaker.current_state
    except Exception:
        return "unknown"


def reset_breaker():
    try:
        groq_breaker.close()
    except Exception:
        pass


def force_breaker_open():
    try:
        groq_breaker.open()
    except Exception:
        pass


def call_groq_with_resilience(fn, *args, **kwargs):
    """Groq-call wrapper: breaker gate + 429/5xx-only retry (<=3).

    Raises pybreaker.CircuitBreakerError immediately when open (caller must
    fail closed to template). 429s never trip the breaker (excluded).
    """
    return groq_breaker.call(call_with_retry, fn, *args, **kwargs)


def breaker_latency_probe():
    """Bounded no-op probe: returns ms for a breaker-gated trivial call."""
    t0 = time.perf_counter()
    try:
        try:
            groq_breaker.call(lambda: None)
        except pybreaker.CircuitBreakerError:
            pass
        except Exception:
            pass
    finally:
        return round((time.perf_counter() - t0) * 1000, 2)
