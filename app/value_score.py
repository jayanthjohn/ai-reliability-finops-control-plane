"""Value and Prompt ROI scoring."""

from __future__ import annotations

from app.models import GenerateRequest, LlmResponse, ValueResult


def business_value_weight(user_tier: str, sla_tier: str) -> float:
    """Return the business value multiplier used for normalized value scoring."""
    if user_tier == "premium":
        base = 10.0
    elif user_tier == "standard":
        base = 5.0
    elif user_tier == "internal":
        base = 2.0
    else:
        base = 1.5
    if sla_tier == "critical":
        return max(base, 8.0)
    if sla_tier == "low":
        return max(1.0, base * 0.8)
    return base


def _business_outcome_value(request: GenerateRequest, success: bool) -> float:
    if not success:
        return 0.1
    endpoint_bonus = 2.0 if any(term in request.endpoint_name.lower() for term in ["customer", "support", "checkout"]) else 1.0
    team_bonus = 1.4 if request.team.lower() in {"sales", "support", "growth"} else 1.0
    return business_value_weight(request.user_tier, request.sla_tier) * endpoint_bonus * team_bonus


def compute_value_score(request: GenerateRequest, response: LlmResponse, quality_score: float, risk_score: int) -> ValueResult:
    """Compute normalized value and ROI from quality, business weight, cost, latency, and risk."""
    weight = business_value_weight(request.user_tier, request.sla_tier)
    normalized_cost = min(2.0, response.estimated_cost / 0.01)
    latency_penalty = min(2.0, response.latency_ms / 3000)
    risk_penalty = risk_score / 100
    raw = (quality_score * weight) / (1 + normalized_cost + latency_penalty + risk_penalty)
    value_score = max(0.0, min(1.0, raw / 10))
    latency_cost = (response.latency_ms / 1000) * 0.0001
    outcome_value = _business_outcome_value(request, quality_score >= 0.55)
    roi = outcome_value / max(0.000001, response.estimated_cost + latency_cost)
    return ValueResult(
        value_score=round(value_score, 4),
        prompt_roi_score=round(roi, 4),
        business_value_weight=weight,
    )

