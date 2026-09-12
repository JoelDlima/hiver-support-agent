"""Phase 4A: OTel SDK (no collector) JSONL file exporter + structlog JSON wiring.

Spans: classify -> retrieve -> draft -> escalate (+ parent predict), with
gen_ai.* attrs + request_id. Exported via BatchSpanProcessor to a JSONL file
(data/traces.jsonl by default, overridable via HIVER_TRACES_PATH).
No collector, no network: file-only, fail-closed (tracing never breaks predict).
"""

import json
import logging
import os
import threading
import time
from pathlib import Path

_TRACES_DEFAULT = Path(__file__).resolve().parent.parent / "data" / "traces.jsonl"

_lock = threading.Lock()
_initialized = False
_tracer_provider = None
_span_processor = None
_traces_path = None


def traces_path():
    """Resolve the JSONL traces path (env override supported)."""
    try:
        env = os.environ.get("HIVER_TRACES_PATH", "").strip()
        if env:
            return Path(env)
    except Exception:
        pass
    return _TRACES_DEFAULT


class JSONLSpanExporter:
    """Minimal OTel SpanExporter writing one JSON object per span per line."""

    def __init__(self, path=None):
        try:
            self.path = Path(path) if path else traces_path()
        except Exception:
            self.path = _TRACES_DEFAULT
        self._wlock = threading.Lock()

    def export(self, spans):
        try:
            from opentelemetry.sdk.trace.export import SpanExportResult
        except Exception:
            SpanExportResult = None
        try:
            lines = []
            for s in spans or []:
                try:
                    ctx = s.get_span_context() if hasattr(s, "get_span_context") else None
                    parent = getattr(s, "parent", None)
                    attrs = dict(getattr(s, "attributes", {}) or {})
                    # Redact anything that looks like a key (never log secrets).
                    for k, v in list(attrs.items()):
                        try:
                            sv = str(v)
                            if "gsk_" in sv or "sk-" in sv:
                                attrs[k] = "[REDACTED]"
                        except Exception:
                            continue
                    try:
                        start_ns = getattr(s, "start_time", None)
                        end_ns = getattr(s, "end_time", None)
                        dur_ms = None
                        if start_ns and end_ns:
                            dur_ms = round((end_ns - start_ns) / 1e6, 2)
                    except Exception:
                        dur_ms = None
                    try:
                        status = getattr(s, "status", None)
                        status_code = str(getattr(status, "status_code", "")) if status else ""
                    except Exception:
                        status_code = ""
                    lines.append(json.dumps({
                        "trace_id": format(ctx.trace_id, "032x") if ctx else "",
                        "span_id": format(ctx.span_id, "016x") if ctx else "",
                        "parent_span_id": format(parent.span_id, "016x") if parent and getattr(parent, "span_id", None) else "",
                        "name": getattr(s, "name", ""),
                        "start_time_ns": start_ns,
                        "end_time_ns": end_ns,
                        "duration_ms": dur_ms,
                        "attributes": attrs,
                        "status": status_code,
                        "service": "hiver",
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }))
                except Exception:
                    continue
            if lines:
                try:
                    self.path.parent.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass
                with self._wlock:
                    with open(self.path, "a", encoding="utf-8") as f:
                        for ln in lines:
                            f.write(ln + "\n")
        except Exception:
            pass
        try:
            return SpanExportResult.SUCCESS
        except Exception:
            return 0

    def shutdown(self):
        return None

    def force_flush(self, timeout_millis=5000):
        return True


def configure_structlog():
    """Wire structlog JSON rendering (idempotent, never raises)."""
    try:
        import structlog

        if getattr(configure_structlog, "_done", False):
            return
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        configure_structlog._done = True
    except Exception:
        pass


def init_tracing(service_name="hiver"):
    """Init OTel TracerProvider + BatchSpanProcessor(JSONL) once. Returns tracer."""
    global _initialized, _tracer_provider, _span_processor, _traces_path
    configure_structlog()
    with _lock:
        if _initialized:
            try:
                from opentelemetry import trace as _trace

                return _trace.get_tracer("hiver")
            except Exception:
                return None
        try:
            from opentelemetry import trace as _trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            path = traces_path()
            _traces_path = path
            exporter = JSONLSpanExporter(path)
            try:
                provider = TracerProvider()
            except Exception:
                provider = None
            if provider is not None:
                try:
                    _trace.set_tracer_provider(provider)
                except Exception:
                    # Provider already set (e.g., by instrumentation): reuse it.
                    try:
                        provider = _trace.get_tracer_provider()
                    except Exception:
                        provider = None
                if provider is not None:
                    try:
                        _span_processor = BatchSpanProcessor(
                            exporter, schedule_delay_millis=200
                        )
                        provider.add_span_processor(_span_processor)
                    except Exception:
                        pass
                    _tracer_provider = provider
            _initialized = True
            try:
                return _trace.get_tracer("hiver")
            except Exception:
                return None
        except Exception:
            _initialized = True
            return None


def get_tracer(name="hiver"):
    try:
        if not _initialized:
            return init_tracing()
        from opentelemetry import trace as _trace

        return _trace.get_tracer(name)
    except Exception:
        return None


def force_flush(timeout_millis=5000):
    try:
        if _span_processor is not None:
            return _span_processor.force_flush(timeout_millis=timeout_millis)
        try:
            from opentelemetry import trace as _trace

            prov = _trace.get_tracer_provider()
            if hasattr(prov, "force_flush"):
                return prov.force_flush(timeout_millis=timeout_millis)
        except Exception:
            pass
    except Exception:
        pass
    return False


def get_logger(request_id=None, **kw):
    """structlog JSON logger with bound request_id (never raises)."""
    try:
        import structlog

        configure_structlog()
        logger = structlog.get_logger("hiver")
        if request_id:
            try:
                return logger.bind(request_id=str(request_id), **kw)
            except Exception:
                return logger
        if kw:
            try:
                return logger.bind(**kw)
            except Exception:
                return logger
        return logger
    except Exception:
        return logging.getLogger("hiver")


def emit_pipeline_spans(request_id, brand, intent, signals, model=None):
    """Emit parent predict span + classify/retrieve/draft/escalate children.

    Fail-closed: never raises. Uses signal timings as attributes.
    """
    try:
        tracer = get_tracer()
        if tracer is None:
            return
        sig = signals if isinstance(signals, dict) else {}
        try:
            model_name = model or "qwen/qwen3.8-27b"
        except Exception:
            model_name = "qwen/qwen3.8-27b"
        try:
            draft_path = str(sig.get("draft_path", "template"))
        except Exception:
            draft_path = "template"
        base_attrs = {
            "request_id": str(request_id or ""),
            "brand": str(brand or ""),
            "gen_ai.request.model": str(model_name),
            "gen_ai.response.id": str(request_id or ""),
        }
        stages = (
            ("classify", sig.get("classify_ms")),
            ("retrieve", sig.get("retrieve_ms")),
            ("draft", sig.get("draft_ms")),
            ("escalate", sig.get("latency_ms", sig.get("escalate_ms"))),
        )
        try:
            with tracer.start_as_current_span(
                "predict",
                attributes={
                    **base_attrs,
                    "gen_ai.operation.name": "predict",
                    "gen_ai.prompt.intent": str(intent or ""),
                    "gen_ai.response.draft_path": draft_path,
                },
            ):
                for stage, ms in stages:
                    try:
                        attrs = {
                            **base_attrs,
                            "gen_ai.operation.name": stage,
                            "gen_ai.prompt.intent": str(intent or ""),
                        }
                        try:
                            if ms is not None:
                                attrs["gen_ai.latency_ms"] = float(ms)
                        except Exception:
                            pass
                        if stage == "draft":
                            attrs["gen_ai.response.draft_path"] = draft_path
                        with tracer.start_as_current_span(stage, attributes=attrs):
                            pass
                    except Exception:
                        continue
        except Exception:
            pass
    except Exception:
        pass
