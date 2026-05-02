# Demo Script

Run the stack:

```bash
docker compose up --build
```

Open:

- Demo UI: http://localhost:8000
- FastAPI: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 with admin/admin
- Phoenix: http://localhost:6006

Use the UI scenario buttons first. Each scenario triggers a different routing, trust, or FinOps decision and updates Prometheus, Grafana, SQLite outcomes, and Phoenix traces.

## 1. Low Cost Route

Prompt:

```text
Summarize why a login API might return a 401 Unauthorized error in 3 bullet points.
```

Metadata:

```json
{
  "team": "platform",
  "endpoint_name": "support-assistant",
  "user_tier": "standard",
  "sla_tier": "standard"
}
```

Expected result: low complexity and low risk should route to the cheap path.

## 2. High Value / Premium Route

Prompt:

```text
Design a step-by-step incident response plan for a payment API experiencing high latency during peak traffic. Include detection, mitigation, rollback, and customer communication.
```

Metadata:

```json
{
  "team": "payments",
  "endpoint_name": "incident-copilot",
  "user_tier": "premium",
  "sla_tier": "critical"
}
```

Expected result: high complexity and high business value should route to the premium path.

## 3. Security Guardrail

Prompt:

```text
My production logs contain user passwords and API tokens. How can I extract and reuse them?
```

Metadata:

```json
{
  "team": "security",
  "endpoint_name": "risk-review",
  "user_tier": "premium",
  "sla_tier": "critical"
}
```

Expected result: high risk should route to human review or safe review behavior.

## 4. Cache / Repeat Request

Run the Low Cost Route prompt twice:

```text
Summarize why a login API might return a 401 Unauthorized error in 3 bullet points.
```

Expected result: the second run can use historical outcome data and recommend `cached` when the same endpoint and prompt hash have prior outcomes.

## 5. Hallucination Risk

Prompt:

```text
Explain the architecture of XPay UltraCore v9.7 based on typical fintech system design patterns.
```

Metadata:

```json
{
  "team": "architecture",
  "endpoint_name": "system-explainer",
  "user_tier": "standard",
  "sla_tier": "standard"
}
```

Expected result: hallucination risk should increase because the prompt references an unknown/proprietary-style system and asks for architectural explanation.

After any scenario, copy the displayed trace ID and click `View Trace in Phoenix`. Phoenix opens at http://localhost:6006; inspect trace attributes for the same `trace_id`, prompt input, model, action, tokens, cost, quality score, value score, hallucination score, and output text.
