"""Cost attribution tags for outcomes and metrics."""

from __future__ import annotations

from app.models import GenerateRequest


def attribution_tags(request: GenerateRequest, model: str) -> dict[str, str]:
    return {
        "team": request.team,
        "endpoint": request.endpoint_name,
        "model": model,
        "user_tier": request.user_tier,
        "environment": request.environment,
    }

