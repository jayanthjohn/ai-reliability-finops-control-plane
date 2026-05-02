"""Phoenix/OpenTelemetry tracing with a no-fail fallback."""

from __future__ import annotations

import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)
_tracer: Any | None = None


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


def emit_generation_trace(attributes: dict[str, Any]) -> None:
    """Emit trace attributes without storing prompt text or PII."""
    if _tracer is None:
        logger.info("trace_fallback %s", {k: v for k, v in attributes.items() if k != "prompt"})
        return
    with _tracer.start_as_current_span("llm.generate") as span:
        for key, value in attributes.items():
            if isinstance(value, (str, int, float, bool)):
                span.set_attribute(key, value)

