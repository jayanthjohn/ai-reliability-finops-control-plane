from app.hallucination_score import compute_hallucination_score


def test_hallucination_score_low_risk():
    result = compute_hallucination_score(
        "Summarize a support note.",
        "Here is a concise summary.",
        "balanced-model",
        20,
    )
    assert result["hallucination_score"] == 0
    assert result["risk_label"] == "LOW"


def test_hallucination_score_high_risk():
    result = compute_hallucination_score(
        "Design proprietary Ultracore confidential architecture.",
        "The architecture system uses a designed to module pipeline.",
        "llama3.2:1b",
        85,
    )
    assert result["hallucination_score"] == 1.0
    assert result["risk_label"] == "HIGH"

