"""Mock-first LLM client for the local demo."""

from __future__ import annotations

import math
import time
from typing import Any

import httpx

from app.config import Settings
from app.models import LlmResponse


MODEL_QUALITY = {
    "cheap-model": 0.68,
    "balanced-model": 0.82,
    "premium-model": 0.92,
    "safe-review": 0.0,
}


def _token_count(text: str) -> int:
    return max(1, math.ceil(len(text.split()) * 1.25))


def generate_mock_response(prompt: str, model: str, action: str, fallback_used: bool = False, llm_mode: str = "mock") -> LlmResponse:
    if model == "safe-review" or action in {"human_review", "reject_or_block", "throttle"}:
        return LlmResponse(
            model="safe-review",
            text="Request requires review before an LLM call.",
            prompt_tokens=_token_count(prompt),
            completion_tokens=8,
            total_tokens=_token_count(prompt) + 8,
            latency_ms=50,
            estimated_cost=0.0,
            llm_mode=llm_mode,
            fallback_used=fallback_used,
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
        llm_mode=llm_mode,
        fallback_used=fallback_used,
    )


def _ollama_token_counts(payload: dict[str, Any], prompt: str, response_text: str) -> tuple[int, int, int]:
    prompt_tokens = int(payload.get("prompt_eval_count") or _token_count(prompt))
    completion_tokens = int(payload.get("eval_count") or _token_count(response_text))
    total_tokens = prompt_tokens + completion_tokens
    return prompt_tokens, completion_tokens, total_tokens


def generate_ollama_response(prompt: str, settings: Settings) -> LlmResponse:
    started = time.perf_counter()
    response = httpx.post(
        f"{settings.ollama_base_url.rstrip('/')}/api/generate",
        json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()
    text = str(payload.get("response") or "").strip()
    if not text:
        text = "Ollama returned an empty response."
    prompt_tokens, completion_tokens, total_tokens = _ollama_token_counts(payload, prompt, text)
    latency_ms = round((time.perf_counter() - started) * 1000)
    return LlmResponse(
        model=str(payload.get("model") or settings.ollama_model),
        text=text,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        estimated_cost=0.0,
        llm_mode="ollama",
        fallback_used=False,
    )


def generate_response(prompt: str, model: str, action: str, settings: Settings) -> LlmResponse:
    if settings.llm_mode == "ollama" and model != "safe-review" and action not in {"human_review", "reject_or_block", "throttle"}:
        try:
            return generate_ollama_response(prompt, settings)
        except Exception:
            return generate_mock_response(prompt, model, action, fallback_used=True, llm_mode="ollama")
    return generate_mock_response(prompt, model, action)
