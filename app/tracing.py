"""Phoenix/OpenTelemetry tracing with a no-fail fallback."""

from __future__ import annotations

from contextlib import contextmanager
import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)
_tracer: Any | None = None


PHOENIX_ATTRIBUTE_MAP = {
    "prompt": "input.value",
    "response_text": "output.value",
    "selected_model": "llm.model_name",
    "model": "gen_ai.response.model",
    "prompt_tokens": "llm.token_count.prompt",
    "completion_tokens": "llm.token_count.completion",
    "total_tokens": "llm.token_count.total",
    "estimated_cost": "llm.cost.total",
    "latency_ms": "llm.latency_ms",
    "llm_mode": "gen_ai.system",
}


def setup_tracing() -> None:
    """Best-effort tracing setup; app startup must not depend on Phoenix."""
    global _tracer
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        settings = get_settings()
        provider = TracerProvider(resource=Resource.create({"service.name": settings.service_name}))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.phoenix_endpoint)))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(settings.service_name)
    except Exception as exc:  # pragma: no cover - depends on optional runtime wiring
        logger.warning("Phoenix tracing disabled: %s", exc)
        _tracer = None


def _safe_log_attributes(attributes: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in attributes.items() if k not in {"prompt", "response_text", "input.value", "output.value"}}


def _set_span_attributes(span: Any, attributes: dict[str, Any]) -> None:
    for key, value in attributes.items():
        if isinstance(value, list):
            value = ",".join(str(item) for item in value)
        if isinstance(value, (str, int, float, bool)):
            span.set_attribute(key, value)
            phoenix_key = PHOENIX_ATTRIBUTE_MAP.get(key)
            if phoenix_key:
                span.set_attribute(phoenix_key, value)


def _mark_span_as_llm(span: Any) -> None:
    span.set_attribute("openinference.span.kind", "LLM")
    span.set_attribute("span.kind", "LLM")
    span.set_attribute("gen_ai.operation.name", "chat")


@contextmanager
def generation_span(initial_attributes: dict[str, Any]):
    """Create a rich LLM span around the full /generate execution."""
    safe_attributes = dict(initial_attributes)
    if _tracer is None:
        logger.info("trace_fallback_start %s", _safe_log_attributes(safe_attributes))
        try:
            yield None
        except Exception:
            logger.exception("trace_fallback_error %s", _safe_log_attributes(safe_attributes))
            raise
        return

    from opentelemetry import trace
    from opentelemetry.trace import SpanKind, Status, StatusCode

    span_name = f"llm.generate.{safe_attributes.get('trace_id', 'unlinked')}"
    with _tracer.start_as_current_span(span_name, kind=SpanKind.CLIENT) as span:
        _mark_span_as_llm(span)
        _set_span_attributes(span, safe_attributes)
        try:
            yield span
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
        finally:
            current_span = trace.get_current_span()
            if current_span is not span:
                logger.debug("generation span context changed before finish")


def enrich_generation_span(span: Any | None, attributes: dict[str, Any]) -> None:
    """Attach LLM input, output, scoring, routing, and cost attributes."""
    if span is None:
        logger.info("trace_fallback_enrich %s", _safe_log_attributes(attributes))
        return
    _set_span_attributes(span, attributes)


def emit_generation_trace(attributes: dict[str, Any], error: Exception | None = None) -> None:
    """Compatibility helper for tests and non-context tracing callers."""
    safe_attributes = dict(attributes)
    if _tracer is None:
        event = "trace_fallback_error" if error else "trace_fallback"
        logger.info("%s %s", event, _safe_log_attributes(safe_attributes))
        return
    try:
        from opentelemetry.trace import SpanKind, Status, StatusCode

        span_name = f"llm.generate.{safe_attributes.get('trace_id', 'unlinked')}"
        with _tracer.start_as_current_span(span_name, kind=SpanKind.CLIENT) as span:
            _mark_span_as_llm(span)
            _set_span_attributes(span, safe_attributes)
            if error is not None:
                span.record_exception(error)
                span.set_status(Status(StatusCode.ERROR, str(error)))
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning("Phoenix tracing emit failed: %s", exc)
