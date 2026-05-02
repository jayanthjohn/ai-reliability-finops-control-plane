"""Heuristic hallucination risk scoring for offline LLM responses."""

from __future__ import annotations


def hallucination_risk_label(score: float) -> str:
    if score > 0.7:
        return "HIGH"
    if score > 0.4:
        return "MEDIUM"
    return "LOW"


def compute_hallucination_score(prompt: str, response: str, model_name: str, complexity_score: int) -> dict[str, float | str]:
    """Compute deterministic hallucination risk for local/offline LLM responses."""
    score = 0.0

    if any(word in prompt.lower() for word in ["ultracore", "proprietary", "confidential"]):
        score += 0.3

    if "cheap" in model_name.lower() or "1b" in model_name.lower():
        score += 0.2

    if complexity_score > 60:
        score += 0.2

    confident_words = ["architecture", "system uses", "designed to", "module", "pipeline"]
    if any(word in response.lower() for word in confident_words):
        score += 0.3

    final_score = min(score, 1.0)
    return {
        "hallucination_score": round(final_score, 4),
        "risk_label": hallucination_risk_label(final_score),
    }

