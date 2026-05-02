from fastapi.testclient import TestClient
from uuid import UUID

import app.main as main
from app.main import app


client = TestClient(app)


def test_ui_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Reliability, Quality & FinOps Control Plane" in response.text
    assert "Decision Panel" in response.text
    assert "Demo Scenarios" in response.text
    assert "Simple request" in response.text
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
            "prompt": "Summarize a short customer support note.",
            "team": "support",
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
    assert body["classification"]
    assert body["decision"]
    assert body["llm_response"]
    assert body["quality"]
    assert body["value"]
    assert body["outcome_id"]


def test_generate_trace_id_is_emitted(monkeypatch):
    emitted = {}

    def capture_trace(attributes):
        emitted.update(attributes)

    monkeypatch.setattr(main, "emit_generation_trace", capture_trace)
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
    assert emitted["endpoint"] == "support-assistant"
    assert emitted["model"] == body["llm_response"]["model"]
    assert emitted["action"] == body["decision"]["selected_action"]
    assert emitted["tokens"] == body["llm_response"]["total_tokens"]
    assert emitted["cost"] == body["llm_response"]["estimated_cost"]
    assert emitted["quality_score"] == body["quality"]["quality_score"]
    assert emitted["value_score"] == body["value"]["value_score"]


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
        "prompt": "Debug and compare retry failure logs for the incident workflow.",
        "team": "platform",
        "endpoint_name": "incident-copilot",
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
