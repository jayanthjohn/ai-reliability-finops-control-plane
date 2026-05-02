"""Prometheus metrics for the control plane."""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

from app.models import ClassificationResult, DecisionResult, GenerateRequest, LlmResponse, QualityResult, ValueResult


REQUESTS = Counter("llm_requests_total", "LLM requests", ["team", "endpoint", "model", "action"])
LATENCY = Histogram("llm_latency_seconds", "LLM latency", ["team", "endpoint", "model"])
TOKENS = Counter("llm_tokens_total", "LLM tokens", ["team", "endpoint", "model", "type"])
COST = Counter("llm_cost_estimated_total", "Estimated LLM cost", ["team", "endpoint", "model"])
QUALITY = Gauge("llm_quality_score", "Latest quality score", ["team", "endpoint", "model"])
VALUE = Gauge("llm_value_score", "Latest value score", ["team", "endpoint", "model"])
ROI = Gauge("llm_prompt_roi_score", "Latest prompt ROI score", ["team", "endpoint", "model"])
COMPLEXITY = Gauge("llm_request_complexity_score", "Latest request complexity score", ["team", "endpoint"])
RISK = Gauge("llm_request_risk_score", "Latest request risk score", ["team", "endpoint"])
BUSINESS_VALUE = Gauge("llm_business_value_score", "Latest business value score", ["team", "endpoint"])
DECISIONS = Counter("llm_decision_actions_total", "Decision actions", ["team", "endpoint", "action"])
ERRORS = Counter("llm_errors_total", "LLM errors", ["team", "endpoint"])


def record_success(
    request: GenerateRequest,
    classification: ClassificationResult,
    decision: DecisionResult,
    response: LlmResponse,
    quality: QualityResult,
    value: ValueResult,
) -> None:
    labels = (request.team, request.endpoint_name, response.model)
    REQUESTS.labels(*labels, decision.selected_action).inc()
    LATENCY.labels(*labels).observe(response.latency_ms / 1000)
    TOKENS.labels(*labels, "prompt").inc(response.prompt_tokens)
    TOKENS.labels(*labels, "completion").inc(response.completion_tokens)
    TOKENS.labels(*labels, "total").inc(response.total_tokens)
    COST.labels(*labels).inc(response.estimated_cost)
    QUALITY.labels(*labels).set(quality.quality_score)
    VALUE.labels(*labels).set(value.value_score)
    ROI.labels(*labels).set(value.prompt_roi_score)
    COMPLEXITY.labels(request.team, request.endpoint_name).set(classification.complexity_score)
    RISK.labels(request.team, request.endpoint_name).set(classification.risk_score)
    BUSINESS_VALUE.labels(request.team, request.endpoint_name).set(classification.business_value_score)
    DECISIONS.labels(request.team, request.endpoint_name, decision.selected_action).inc()


def record_error(team: str, endpoint: str) -> None:
    ERRORS.labels(team, endpoint).inc()

