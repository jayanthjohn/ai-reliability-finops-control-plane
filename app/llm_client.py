"""Mock-first LLM client for the local demo."""

from __future__ import annotations

import math

from app.models import LlmResponse


MODEL_QUALITY = {
    "cheap-model": 0.68,
    "balanced-model": 0.82,
    "premium-model": 0.92,
    "safe-review": 0.0,
}


def _token_count(text: str) -> int:
    return max(1, math.ceil(len(text.split()) * 1.25))


def generate_mock_response(prompt: str, model: str, action: str) -> LlmResponse:
    if model == "safe-review" or action in {"human_review", "reject_or_block", "throttle"}:
        return LlmResponse(
            model="safe-review",
            text="Request requires review before an LLM call.",
            prompt_tokens=_token_count(prompt),
            completion_tokens=8,
            total_tokens=_token_count(prompt) + 8,
            latency_ms=50,
            estimated_cost=0.0,
        )

    prompt_tokens = _token_count(prompt)
    completion_tokens = max(24, min(180, prompt_tokens * 2))
    latency = {"cheap-model": 420, "balanced-model": 850, "premium-model": 1350}[model]
    price_per_1k = {"cheap-model": 0.0004, "balanced-model": 0.0015, "premium-model": 0.006}[model]
    total_tokens = prompt_tokens + completion_tokens
    cost = (total_tokens / 1000) * price_per_1k
    text = (
        f"Mock {model} response: I processed the request and produced a concise answer "
        f"focused on {prompt.split()[0].lower()} with action {action}."
    )
    return LlmResponse(
        model=model,
        text=text,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=latency,
        estimated_cost=round(cost, 6),
    )

