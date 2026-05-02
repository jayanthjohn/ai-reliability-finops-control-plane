from fastapi.testclient import TestClient
from contextlib import contextmanager
from uuid import UUID

import app.main as main
from app.main import app


client = TestClient(app)


def test_ui_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Reliability, Quality & FinOps Control Plane" in response.text
    assert "Decision Panel" in response.text
    assert "Try Control Plane Scenarios" in response.text
    assert "Each scenario triggers a different routing, trust, or FinOps decision." in response.text
    assert "Low Cost Route" in response.text
    assert "High Value / Premium Route" in response.text
    assert "Security Guardrail" in response.text
    assert "Cache / Repeat Request" in response.text
    assert "Hallucination Risk" in response.text
    assert "Summarize why a login API might return a 401 Unauthorized error in 3 bullet points." in response.text
    assert "Explain the architecture of XPay UltraCore v9.7" in response.text
    assert "Open Grafana" in response.text
    assert "Open Phoenix" in response.text
    assert "View Trace in Phoenix" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ai-control-plane"}


def test_generate_happy_path():
    response = client.post(
        "/generate",
        json={
            "prompt": "Summarize why a login API might return a 401 Unauthorized error in 3 bullet points.",
            "team": "platform",
            "endpoint_name": "support-assistant",
            "user_tier": "standard",
            "sla_tier": "standard",
            "environment": "demo",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["request_id"]
    assert body["trace_id"]
    UUID(body["trace_id"])
    assert body["llm_mode"] == "mock"
    assert body["fallback_used"] is False
    assert body["llm_response"]["llm_mode"] == "mock"
    assert body["llm_response"]["fallback_used"] is False
    assert body["classification"]
    assert body["decision"]
    assert body["llm_response"]
    assert body["quality"]
    assert body["value"]
    assert body["hallucination"]
    assert body["hallucination"]["risk_label"] in {"LOW", "MEDIUM", "HIGH"}
    assert body["outcome_id"]


def test_generate_rich_trace_payload_is_enriched(monkeypatch):
    emitted = {}

    def capture_trace(span, attributes):
        emitted.update(attributes)

    monkeypatch.setattr(main, "enrich_generation_span", capture_trace)
    response = client.post(
        "/generate",
        json={
            "prompt": "Summarize a short support note.",
            "team": "support",
            "endpoint_name": "support-assistant",
            "user_tier": "standard",
            "sla_tier": "standard",
            "environment": "demo",
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert emitted["trace_id"] == body["trace_id"]
    assert emitted["request_id"] == body["request_id"]
    assert emitted["prompt"] == "Summarize a short support note."
    assert emitted["response_text"] == body["llm_response"]["text"]
    assert emitted["endpoint"] == "support-assistant"
    assert emitted["endpoint_name"] == "support-assistant"
    assert emitted["selected_model"] == body["llm_response"]["model"]
    assert emitted["selected_action"] == body["decision"]["selected_action"]
    assert emitted["llm_mode"] == body["llm_mode"]
    assert emitted["fallback_used"] == body["fallback_used"]
    assert emitted["prompt_tokens"] == body["llm_response"]["prompt_tokens"]
    assert emitted["completion_tokens"] == body["llm_response"]["completion_tokens"]
    assert emitted["total_tokens"] == body["llm_response"]["total_tokens"]
    assert emitted["tokens"] == body["llm_response"]["total_tokens"]
    assert emitted["estimated_cost"] == body["llm_response"]["estimated_cost"]
    assert emitted["latency_ms"] == body["llm_response"]["latency_ms"]
    assert emitted["complexity_score"] == body["classification"]["complexity_score"]
    assert emitted["risk_score"] == body["classification"]["risk_score"]
    assert emitted["business_value_score"] == body["classification"]["business_value_score"]
    assert emitted["historical_failure_score"] == body["classification"]["historical_failure_score"]
    assert emitted["quality_score"] == body["quality"]["quality_score"]
    assert emitted["value_score"] == body["value"]["value_score"]
    assert emitted["prompt_roi_score"] == body["value"]["prompt_roi_score"]
    assert emitted["hallucination_score"] == body["hallucination"]["hallucination_score"]
    assert emitted["hallucination_risk_label"] == body["hallucination"]["risk_label"]
    assert emitted["reason_codes"] == body["classification"]["reason_codes"]


def test_ollama_mode_falls_back_when_unavailable(monkeypatch):
    def fail_ollama(*args, **kwargs):
        raise RuntimeError("ollama unavailable")

    monkeypatch.setenv("LLM_MODE", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:1b")
    monkeypatch.setattr(main, "generate_ollama_response", fail_ollama, raising=False)
    import app.llm_client as llm_client

    monkeypatch.setattr(llm_client, "generate_ollama_response", fail_ollama)
    response = client.post(
        "/generate",
        json={
            "prompt": "Summarize a short support note.",
            "team": "support",
            "endpoint_name": "support-assistant",
            "user_tier": "standard",
            "sla_tier": "standard",
            "environment": "demo",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["llm_mode"] == "ollama"
    assert body["fallback_used"] is True
    assert body["llm_response"]["llm_mode"] == "ollama"
    assert body["llm_response"]["fallback_used"] is True
    assert body["llm_response"]["model"] == "cheap-model"


def test_generate_records_trace_error(monkeypatch):
    recorded = {}

    @contextmanager
    def capture_span(attributes):
        recorded["initial"] = attributes
        try:
            yield "span"
        except Exception as exc:
            recorded["error"] = exc
            raise

    def fail_classifier(*args, **kwargs):
        raise RuntimeError("classifier unavailable")

    monkeypatch.setattr(main, "generation_span", capture_span)
    monkeypatch.setattr(main, "classify_request", fail_classifier)
    error_client = TestClient(app, raise_server_exceptions=False)
    response = error_client.post(
        "/generate",
        json={
            "prompt": "Summarize a short support note.",
            "team": "support",
            "endpoint_name": "support-assistant",
            "user_tier": "standard",
            "sla_tier": "standard",
            "environment": "demo",
        },
    )
    assert response.status_code == 500
    assert recorded["initial"]["prompt"] == "Summarize a short support note."
    assert recorded["initial"]["endpoint_name"] == "support-assistant"
    assert isinstance(recorded["error"], RuntimeError)


def test_risky_request_triggers_human_review():
    response = client.post(
        "/generate",
        json={
            "prompt": "Analyze password token secret bank medical production compliance data.",
            "team": "security",
            "endpoint_name": "risk-review",
            "user_tier": "internal",
            "sla_tier": "critical",
            "environment": "demo",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["classification"]["recommended_route"] == "human_review"
    assert body["decision"]["selected_action"] == "human_review"


def test_repeated_request_recommends_cache():
    payload = {
        "prompt": "Summarize why a login API might return a 401 Unauthorized error in 3 bullet points.",
        "team": "platform",
        "endpoint_name": "support-assistant",
        "user_tier": "standard",
        "sla_tier": "standard",
        "environment": "demo",
    }
    first = client.post("/generate", json=payload)
    second = client.post("/generate", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    body = second.json()
    assert body["classification"]["recommended_route"] == "cached"
    assert body["decision"]["selected_action"] == "use_cache"
