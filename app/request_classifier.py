"""Deterministic request intelligence classifier.

The MVP uses cheap heuristics so the classifier always runs before spend. A
production version could replace or augment this with a small local classifier
model while keeping the same pre-request contract.
"""

from __future__ import annotations

import hashlib
import re

from app.config import BudgetState, SloState
from app.models import ClassificationResult, GenerateRequest
from app.outcome_store import get_historical_failure_score, get_prompt_seen_count


COMPLEXITY_TERMS = {"compare", "analyze", "design", "generate", "debug", "evaluate", "architecture", "multi-step"}
RISK_TERMS = {"pii", "password", "token", "secret", "bank", "medical", "production", "compliance", "ssn", "credential"}
CUSTOMER_ENDPOINT_HINTS = {"chat", "support", "checkout", "customer", "prod", "api"}


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.strip().lower().encode("utf-8")).hexdigest()[:16]


def _contains_any(text: str, terms: set[str]) -> list[str]:
    lowered = text.lower()
    return sorted(term for term in terms if term in lowered)


def _score_complexity(prompt: str) -> tuple[int, list[str]]:
    words = re.findall(r"\w+", prompt.lower())
    score = min(45, len(words) // 4)
    reasons: list[str] = []
    matched = _contains_any(prompt, COMPLEXITY_TERMS)
    if matched:
        score += min(45, len(matched) * 15)
        reasons.append("complexity_terms")
    if len(matched) >= 3:
        score += 10
        reasons.append("multiple_complexity_terms")
    if any(term in prompt.lower() for term in ["step by step", "first", "then", "finally", "tradeoff"]):
        score += 15
        reasons.append("multi_step_language")
    if len(words) > 120:
        score += 15
        reasons.append("long_prompt")
    return min(100, score), reasons


def _score_risk(prompt: str) -> tuple[int, list[str]]:
    matched = _contains_any(prompt, RISK_TERMS)
    score = min(100, len(matched) * 22)
    reasons = ["risk_terms"] if matched else []
    if "do not log" in prompt.lower() or "redact" in prompt.lower():
        score += 10
        reasons.append("sensitive_handling_requested")
    return min(100, score), reasons


def _score_business_value(request: GenerateRequest) -> tuple[int, list[str]]:
    score = 20
    reasons: list[str] = []
    if request.user_tier == "premium":
        score += 35
        reasons.append("premium_user")
    elif request.user_tier == "standard":
        score += 18
        reasons.append("standard_user")
    elif request.user_tier == "internal":
        score += 8
        reasons.append("internal_user")
    if request.sla_tier == "critical":
        score += 35
        reasons.append("critical_sla")
    elif request.sla_tier == "standard":
        score += 15
        reasons.append("standard_sla")
    endpoint = request.endpoint_name.lower()
    if any(hint in endpoint for hint in CUSTOMER_ENDPOINT_HINTS):
        score += 15
        reasons.append("customer_facing_endpoint")
    return min(100, score), reasons


def classify_request(request: GenerateRequest, budget_state: BudgetState, slo_state: SloState) -> ClassificationResult:
    """Classify request complexity, risk, value, history, and route before LLM spend."""
    complexity, complexity_reasons = _score_complexity(request.prompt)
    risk, risk_reasons = _score_risk(request.prompt)
    business_value, value_reasons = _score_business_value(request)
    hashed_prompt = prompt_hash(request.prompt)
    historical_failure = get_historical_failure_score(request.endpoint_name, hashed_prompt)
    prompt_seen_count = get_prompt_seen_count(request.endpoint_name, hashed_prompt)

    reason_codes = complexity_reasons + risk_reasons + value_reasons
    if historical_failure > 0:
        reason_codes.append("historical_failures")
    if budget_state.pressure == "high":
        reason_codes.append("budget_pressure_high")
    if slo_state.at_risk:
        reason_codes.append("slo_at_risk")

    repeated_prompt = prompt_seen_count > 0
    if repeated_prompt:
        reason_codes.append("repeated_prompt")
    if risk >= 80:
        route = "human_review"
    elif repeated_prompt and risk < 60:
        route = "cached"
    elif complexity >= 70 and business_value >= 70:
        route = "premium"
    elif complexity <= 35 and risk <= 40:
        route = "cheap"
    else:
        route = "balanced"

    confidence = 0.72
    if route in {"human_review", "cheap"}:
        confidence += 0.12
    if reason_codes:
        confidence += min(0.1, len(reason_codes) * 0.02)

    return ClassificationResult(
        complexity_score=complexity,
        risk_score=risk,
        business_value_score=business_value,
        historical_failure_score=historical_failure,
        recommended_route=route,
        confidence=round(min(0.98, confidence), 2),
        reason_codes=reason_codes,
    )
