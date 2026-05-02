"""Pre-request decision engine for model routing and controls."""

from __future__ import annotations

from app.config import BudgetState, SloState
from app.models import ClassificationResult, DecisionResult


MODEL_PROFILES = {
    "cheap-model": {"cost": 0.0006, "latency_ms": 450},
    "balanced-model": {"cost": 0.0025, "latency_ms": 900},
    "premium-model": {"cost": 0.008, "latency_ms": 1500},
    "safe-review": {"cost": 0.0, "latency_ms": 50},
}
ALLOWED_MODELS = set(MODEL_PROFILES)


def _result(action: str, model: str, rationale: list[str]) -> DecisionResult:
    profile = MODEL_PROFILES[model]
    return DecisionResult(
        selected_action=action,
        selected_model=model,
        expected_cost=profile["cost"],
        expected_latency_ms=profile["latency_ms"],
        rationale=rationale,
    )


def decide_route(
    classification: ClassificationResult,
    budget_state: BudgetState,
    slo_state: SloState,
    preferred_model: str | None = None,
) -> DecisionResult:
    """Choose the best action before spending on an LLM call."""
    rationale: list[str] = []

    if classification.risk_score >= 80:
        return _result("human_review", "safe-review", ["risk_score_above_policy_threshold"])

    if classification.historical_failure_score >= 80:
        return _result("human_review", "safe-review", ["historical_failure_score_high"])

    if budget_state.pressure == "high" and classification.business_value_score < 45:
        if classification.complexity_score > 75:
            return _result("throttle", "safe-review", ["budget_pressure_high", "low_business_value", "high_complexity"])
        rationale.extend(["budget_pressure_high", "low_business_value"])
        return _result("route_to_cheap_model", "cheap-model", rationale)

    if classification.historical_failure_score >= 50:
        rationale.append("historical_failure_score_elevated")
        return _result("route_to_premium_model", "premium-model", rationale)

    if classification.recommended_route == "cached":
        return _result("use_cache", "cheap-model", ["repeated_prompt_seen_before"])

    if preferred_model:
        if preferred_model not in ALLOWED_MODELS or preferred_model == "safe-review":
            return _result("reject_or_block", "safe-review", ["preferred_model_not_allowed"])
        if preferred_model == "premium-model" and classification.business_value_score < 50:
            return _result("route_to_balanced_model", "balanced-model", ["preferred_model_downgraded_by_value_policy"])
        return _result(f"route_to_{preferred_model.replace('-model', '')}_model", preferred_model, ["preferred_model_allowed"])

    if slo_state.at_risk and classification.business_value_score >= 70:
        return _result("route_to_balanced_model", "balanced-model", ["slo_at_risk", "high_business_value"])

    if classification.complexity_score >= 70 and classification.business_value_score >= 70:
        return _result("route_to_premium_model", "premium-model", ["high_complexity", "high_business_value"])

    if classification.complexity_score <= 35 and classification.risk_score <= 40:
        return _result("route_to_cheap_model", "cheap-model", ["low_complexity", "low_risk"])

    return _result("route_to_balanced_model", "balanced-model", ["default_balanced_policy"])

