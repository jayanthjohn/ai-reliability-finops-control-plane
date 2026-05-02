from app.config import BudgetState, SloState
from app.models import GenerateRequest
from app.request_classifier import classify_request


def _request(prompt: str, user_tier: str = "free", sla_tier: str = "low") -> GenerateRequest:
    return GenerateRequest(
        prompt=prompt,
        team="platform",
        endpoint_name="support-assistant",
        user_tier=user_tier,
        sla_tier=sla_tier,
        environment="demo",
    )


def test_low_complexity_low_risk_routes_cheap():
    result = classify_request(_request("Summarize this short note."), BudgetState(), SloState())
    assert result.complexity_score <= 35
    assert result.risk_score <= 40
    assert result.recommended_route == "cheap"


def test_complex_premium_request_routes_premium():
    request = _request(
        "Analyze and design a multi-step architecture plan with tradeoffs for customer support.",
        user_tier="premium",
        sla_tier="critical",
    )
    result = classify_request(request, BudgetState(), SloState())
    assert result.complexity_score >= 70
    assert result.business_value_score >= 70
    assert result.recommended_route == "premium"


def test_risky_request_routes_human_review():
    result = classify_request(_request("Process password token bank medical compliance production data."), BudgetState(), SloState())
    assert result.risk_score >= 80
    assert result.recommended_route == "human_review"

