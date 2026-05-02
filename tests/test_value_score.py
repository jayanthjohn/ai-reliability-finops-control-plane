from app.llm_client import generate_mock_response
from app.models import GenerateRequest
from app.value_score import compute_value_score


def test_value_score_output_range():
    request = GenerateRequest(
        prompt="Summarize this",
        team="support",
        endpoint_name="customer-support-chat",
        user_tier="premium",
        sla_tier="critical",
        environment="demo",
    )
    response = generate_mock_response(request.prompt, "premium-model", "route_to_premium_model")
    value = compute_value_score(request, response, 0.9, 10)
    assert 0 <= value.value_score <= 1
    assert value.prompt_roi_score > 0
    assert value.business_value_weight >= 8

