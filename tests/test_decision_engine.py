from app.config import BudgetState, SloState
from app.decision_engine import decide_route
from app.models import ClassificationResult


def _classification(**overrides) -> ClassificationResult:
    data = {
        "complexity_score": 20,
        "risk_score": 10,
        "business_value_score": 30,
        "historical_failure_score": 0,
        "recommended_route": "cheap",
        "confidence": 0.9,
        "reason_codes": [],
    }
    data.update(overrides)
    return ClassificationResult(**data)


def test_risk_triggers_human_review():
    decision = decide_route(_classification(risk_score=85), BudgetState(), SloState())
    assert decision.selected_action == "human_review"
    assert decision.selected_model == "safe-review"


def test_high_complexity_high_value_routes_premium():
    decision = decide_route(
        _classification(complexity_score=80, business_value_score=85, recommended_route="premium"),
        BudgetState(),
        SloState(),
    )
    assert decision.selected_action == "route_to_premium_model"
    assert decision.selected_model == "premium-model"


def test_low_complexity_low_risk_routes_cheap():
    decision = decide_route(_classification(), BudgetState(), SloState())
    assert decision.selected_action == "route_to_cheap_model"
    assert decision.selected_model == "cheap-model"

