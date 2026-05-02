"""Quality scoring for the MVP.

Production systems can plug in LLM-as-Judge, RAGAS, embedding similarity,
human feedback, or domain validators behind this contract. The MVP keeps the
calculation deterministic for local demos and tests.
"""

from __future__ import annotations

import re

from app.llm_client import MODEL_QUALITY
from app.models import LlmResponse, QualityResult


def compute_quality_score(prompt: str, response: LlmResponse, complexity_score: int) -> QualityResult:
    """Compute weighted quality from correctness, relevance, validation, and feedback."""
    if response.model == "safe-review":
        breakdown = {
            "correctness": 0.0,
            "groundedness_relevance": 0.5,
            "domain_rule_validation": 1.0,
            "synthetic_feedback": 0.7,
        }
    else:
        complexity_penalty = max(0.0, (complexity_score - 50) / 200)
        correctness = max(0.1, MODEL_QUALITY.get(response.model, 0.7) - complexity_penalty)
        prompt_terms = {w for w in re.findall(r"\w+", prompt.lower()) if len(w) > 4}
        response_text = response.text.lower()
        matches = sum(1 for term in prompt_terms if term in response_text)
        relevance = min(1.0, matches / max(1, min(5, len(prompt_terms))) + 0.35)
        domain_validation = 0.9 if response.text and "error" not in response_text else 0.35
        synthetic_feedback = 0.88
        breakdown = {
            "correctness": round(correctness, 4),
            "groundedness_relevance": round(relevance, 4),
            "domain_rule_validation": round(domain_validation, 4),
            "synthetic_feedback": synthetic_feedback,
        }
    score = (
        breakdown["correctness"] * 0.40
        + breakdown["groundedness_relevance"] * 0.25
        + breakdown["domain_rule_validation"] * 0.20
        + breakdown["synthetic_feedback"] * 0.15
    )
    return QualityResult(quality_score=round(max(0.0, min(1.0, score)), 4), breakdown=breakdown)

