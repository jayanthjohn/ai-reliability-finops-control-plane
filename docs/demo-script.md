# Demo Script

Run the stack:

```bash
docker compose up --build
```

Open:

- FastAPI: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 with admin/admin
- Phoenix: http://localhost:6006

## 1. Low complexity, low risk -> cheap model

```bash
curl -s http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Summarize this short note for the customer.",
    "team": "support",
    "endpoint_name": "support-assistant",
    "user_tier": "free",
    "sla_tier": "low",
    "environment": "demo"
  }' | jq
```

Expected decision: `route_to_cheap_model`.

## 2. Complex premium request -> premium model

```bash
curl -s http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Analyze and design a multi-step customer retention strategy with tradeoffs, risks, and implementation plan.",
    "team": "growth",
    "endpoint_name": "customer-insights",
    "user_tier": "premium",
    "sla_tier": "critical",
    "environment": "demo"
  }' | jq
```

Expected decision: `route_to_premium_model`.

## 3. Risky request -> human review

```bash
curl -s http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Analyze password token secret bank medical production compliance data.",
    "team": "security",
    "endpoint_name": "risk-review",
    "user_tier": "internal",
    "sla_tier": "critical",
    "environment": "demo"
  }' | jq
```

Expected decision: `human_review` and model `safe-review`.

## 4. Repeated request -> cache recommendation

Run the same request twice:

```bash
curl -s http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Debug and compare these retry failure logs for the incident workflow.",
    "team": "platform",
    "endpoint_name": "incident-copilot",
    "user_tier": "standard",
    "sla_tier": "standard",
    "environment": "demo"
  }' | jq
```

The second run can use historical outcome data and recommend `cached` when the same endpoint and prompt hash have prior outcomes.
