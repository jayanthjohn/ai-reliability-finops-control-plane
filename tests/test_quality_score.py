from app.llm_client import generate_mock_response
from app.quality_score import compute_quality_score


def test_quality_score_output_range():
    response = generate_mock_response("Analyze customer support issue", "balanced-model", "route_to_balanced_model")
    quality = compute_quality_score("Analyze customer support issue", response, 45)
    assert 0 <= quality.quality_score <= 1
    assert "correctness" in quality.breakdown

