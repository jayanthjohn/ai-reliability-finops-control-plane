"""FastAPI application for the AI control plane MVP."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import HTMLResponse, Response

from app.config import get_settings
from app.cost_attribution import attribution_tags
from app.decision_engine import decide_route
from app.hallucination_score import compute_hallucination_score
from app.llm_client import generate_response
from app.metrics import record_error, record_success
from app.models import GenerateRequest, GenerateResponse, OutcomeRecord
from app.outcome_store import get_summary, init_db, save_outcome
from app.quality_score import compute_quality_score
from app.request_classifier import classify_request, prompt_hash
from app.tracing import enrich_generation_span, generation_span, setup_tracing
from app.ui import INDEX_HTML
from app.value_score import compute_value_score


app = FastAPI(title="AI Reliability, Quality & FinOps Control Plane")


@app.on_event("startup")
def startup() -> None:
    init_db()
    setup_tracing()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-control-plane"}


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    settings = get_settings()
    request_id = str(uuid4())
    trace_id = str(uuid4())
    try:
        with generation_span(
            {
                "trace_id": trace_id,
                "request_id": request_id,
                "team": request.team,
                "endpoint": request.endpoint_name,
                "endpoint_name": request.endpoint_name,
                "prompt": request.prompt,
                "llm_mode": settings.llm_mode,
                "ollama_model": settings.ollama_model,
            }
        ) as span:
            classification = classify_request(request, settings.budget_state, settings.slo_state)
            decision = decide_route(classification, settings.budget_state, settings.slo_state, request.preferred_model)
            llm_response = generate_response(request.prompt, decision.selected_model, decision.selected_action, settings)
            quality = compute_quality_score(request.prompt, llm_response, classification.complexity_score)
            value = compute_value_score(request, llm_response, quality.quality_score, classification.risk_score)
            hallucination = compute_hallucination_score(
                request.prompt,
                llm_response.text,
                llm_response.model,
                classification.complexity_score,
            )
            tags = attribution_tags(request, llm_response.model)
            outcome = OutcomeRecord(
                request_id=request_id,
                prompt_hash=prompt_hash(request.prompt),
                team=request.team,
                endpoint_name=request.endpoint_name,
                user_tier=request.user_tier,
                sla_tier=request.sla_tier,
                model=llm_response.model,
                action=decision.selected_action,
                complexity_score=classification.complexity_score,
                risk_score=classification.risk_score,
                business_value_score=classification.business_value_score,
                historical_failure_score=classification.historical_failure_score,
                prompt_tokens=llm_response.prompt_tokens,
                completion_tokens=llm_response.completion_tokens,
                total_tokens=llm_response.total_tokens,
                latency_ms=llm_response.latency_ms,
                estimated_cost=llm_response.estimated_cost,
                quality_score=quality.quality_score,
                value_score=value.value_score,
                prompt_roi_score=value.prompt_roi_score,
                success=quality.quality_score >= 0.55 and decision.selected_action not in {"reject_or_block", "throttle"},
                reason_codes=classification.reason_codes,
                attribution_tags=tags,
            )
            outcome_id = save_outcome(outcome)
            record_success(request, classification, decision, llm_response, quality, value)
            enrich_generation_span(
                span,
                {
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "team": request.team,
                    "endpoint": request.endpoint_name,
                    "endpoint_name": request.endpoint_name,
                    "prompt": request.prompt,
                    "response_text": llm_response.text,
                    "selected_model": llm_response.model,
                    "selected_action": decision.selected_action,
                    "model": llm_response.model,
                    "action": decision.selected_action,
                    "llm_mode": llm_response.llm_mode,
                    "fallback_used": llm_response.fallback_used,
                    "ollama_model": settings.ollama_model,
                    "complexity_score": classification.complexity_score,
                    "risk_score": classification.risk_score,
                    "business_value_score": classification.business_value_score,
                    "historical_failure_score": classification.historical_failure_score,
                    "prompt_tokens": llm_response.prompt_tokens,
                    "completion_tokens": llm_response.completion_tokens,
                    "total_tokens": llm_response.total_tokens,
                    "tokens": llm_response.total_tokens,
                    "estimated_cost": llm_response.estimated_cost,
                    "cost": llm_response.estimated_cost,
                    "latency_ms": llm_response.latency_ms,
                    "latency": llm_response.latency_ms,
                    "quality_score": quality.quality_score,
                    "value_score": value.value_score,
                    "prompt_roi_score": value.prompt_roi_score,
                    "hallucination_score": hallucination["hallucination_score"],
                    "hallucination_risk_label": hallucination["risk_label"],
                    "reason_codes": classification.reason_codes,
                },
            )
            return GenerateResponse(
                request_id=request_id,
                trace_id=trace_id,
                llm_mode=llm_response.llm_mode,
                fallback_used=llm_response.fallback_used,
                classification=classification,
                decision=decision,
                llm_response=llm_response,
                quality=quality,
                value=value,
                hallucination=hallucination,
                outcome_id=outcome_id,
            )
    except Exception:
        record_error(request.team, request.endpoint_name)
        raise


@app.get("/outcomes/summary")
def outcomes_summary() -> dict:
    return get_summary()


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
