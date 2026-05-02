# AI Reliability, Quality & FinOps Control Plane

Lightweight MacBook Air demo for pre-request LLM decisioning.

## North Star

Given everything known about an incoming request, including complexity, user context, SLA, business value, historical quality, and current cost envelope, decide the single best action before spending on the LLM call, then learn from the outcome.

## What Makes This Different

The control plane does not wait until after an expensive model call to reason about quality and cost. It classifies the request first, makes a policy decision, routes to a mock model path or review path, and stores the outcome for a basic feedback loop.

## MacBook Air MVP Scope

Runs locally with Docker Compose:

- Demo chat UI on http://localhost:8000
- FastAPI app on http://localhost:8000/docs
- Prometheus on http://localhost:9090
- Grafana on http://localhost:3000
- Phoenix on http://localhost:6006
- SQLite outcome store
- Mock LLM mode by default

## Architecture Summary

Request flow:

1. User calls `POST /generate`.
2. `request_classifier` scores complexity, risk, business value, and historical failures before any LLM call.
3. `decision_engine` chooses cheap, balanced, premium, cache, review, throttle, or block action.
4. `llm_client` returns a mock model response.
5. `quality_score` computes deterministic quality.
6. `value_score` computes normalized value and Prompt ROI.
7. `outcome_store` persists the result to SQLite.
8. `metrics` exposes Prometheus metrics.
9. `tracing` attempts Phoenix/OpenTelemetry export without blocking app startup.

## What Is Excluded

The MVP intentionally does not include Kafka, NATS, Loki, Mimir, S3, full auth, Jira, ServiceNow, or enterprise chargeback. Enterprise features are roadmap-only for now.

The app does not store secrets or PII in logs, metrics, traces, or SQLite. Prompts are stored only as hashes in the outcome store.

## Setup

```bash
docker compose up --build
```

Then open:

- Demo chat UI: http://localhost:8000
- FastAPI docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 using `admin` / `admin`
- Phoenix: http://localhost:6006

## Demo UI

Open http://localhost:8000 after starting Docker Compose.

Use the chat UI to send a prompt or choose one of the built-in demo scenarios:

- Simple request
- Complex premium request
- Security risk request
- Repeated request

Each chat submission calls `POST /generate`, so it still runs request intelligence, decisioning, mock LLM generation, quality scoring, value scoring, SQLite outcome storage, Prometheus metrics, and Phoenix tracing. After sending a few requests, open Grafana at http://localhost:3000 to see dashboard data and Phoenix at http://localhost:6006 to inspect traces when export is available. If Phoenix export is unavailable, the app logs a tracing fallback and continues running.

## API

Health:

```bash
curl http://localhost:8000/health
```

Generate:

```bash
curl -s http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Summarize this short customer support note.",
    "team": "support",
    "endpoint_name": "support-assistant",
    "user_tier": "standard",
    "sla_tier": "standard",
    "environment": "demo"
  }' | jq
```

Summary:

```bash
curl http://localhost:8000/outcomes/summary
```

Metrics:

```bash
curl http://localhost:8000/metrics
```

## Tests

```bash
pytest
```

## Troubleshooting

- If Grafana has no data, send a few `/generate` requests first and wait for a Prometheus scrape interval.
- If Phoenix traces do not appear, the app still runs. The tracing setup uses a best-effort OTLP exporter and logs a fallback warning if unavailable.
- If local ports are already used, change the host ports in `docker-compose.yml`.
- If SQLite state gets noisy during demos, remove the `app-data` Docker volume.

## Demo Script

See [docs/demo-script.md](docs/demo-script.md).

## Roadmap

Phase 2: SLO-aware Adaptive Budget Engine.

Phase 3: Shadow Routing and Continuous Model Benchmarking.

Phase 4: LLM Resilience and Chaos Testing Suite.
