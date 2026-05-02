"""Shared API and internal data models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


UserTier = Literal["free", "standard", "premium", "internal"]
SlaTier = Literal["low", "standard", "critical"]


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    team: str = Field(..., min_length=1, max_length=64)
    endpoint_name: str = Field(..., min_length=1, max_length=128)
    user_tier: UserTier
    sla_tier: SlaTier
    environment: str = "demo"
    preferred_model: str | None = None


class ClassificationResult(BaseModel):
    complexity_score: int
    risk_score: int
    business_value_score: int
    historical_failure_score: int
    recommended_route: str
    confidence: float
    reason_codes: list[str]


class DecisionResult(BaseModel):
    selected_action: str
    selected_model: str
    expected_cost: float
    expected_latency_ms: int
    rationale: list[str]


class LlmResponse(BaseModel):
    model: str
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    estimated_cost: float
    llm_mode: str = "mock"
    fallback_used: bool = False


class QualityResult(BaseModel):
    quality_score: float
    breakdown: dict[str, float]


class ValueResult(BaseModel):
    value_score: float
    prompt_roi_score: float
    business_value_weight: float


class HallucinationResult(BaseModel):
    hallucination_score: float
    risk_label: Literal["LOW", "MEDIUM", "HIGH"]


class GenerateResponse(BaseModel):
    request_id: str
    trace_id: str
    llm_mode: str
    fallback_used: bool
    classification: ClassificationResult
    decision: DecisionResult
    llm_response: LlmResponse
    quality: QualityResult
    value: ValueResult
    hallucination: HallucinationResult
    outcome_id: str


class OutcomeRecord(BaseModel):
    request_id: str
    prompt_hash: str
    team: str
    endpoint_name: str
    user_tier: str
    sla_tier: str
    model: str
    action: str
    complexity_score: int
    risk_score: int
    business_value_score: int
    historical_failure_score: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    estimated_cost: float
    quality_score: float
    value_score: float
    prompt_roi_score: float
    success: bool
    reason_codes: list[str]
    attribution_tags: dict[str, Any]
