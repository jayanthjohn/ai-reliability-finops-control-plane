from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


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
            "endpoint_name": "customer-support-chat",
            "user_tier": "standard",
            "sla_tier": "standard",
            "environment": "demo",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["request_id"]
    assert body["classification"]
    assert body["decision"]
    assert body["llm_response"]
    assert body["quality"]
    assert body["value"]
    assert body["outcome_id"]


def test_risky_request_triggers_human_review():
    response = client.post(
        "/generate",
        json={
            "prompt": "Analyze password token secret bank medical production compliance data.",
            "team": "security",
            "endpoint_name": "incident-review",
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
        "prompt": "Debug and compare retry failure logs for checkout.",
        "team": "platform",
        "endpoint_name": "checkout-api",
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
