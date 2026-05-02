# AGENTS.md

## Project
AI Reliability, Quality & FinOps Control Plane

## MVP Goal
Build a lightweight MacBook Air demo that proves pre-request decisioning for LLM calls.

The MVP must show:
- Request Intelligence Classifier before any LLM call
- Decision Engine selecting best action/model path before spend
- Quality Score after response
- Value Score / Prompt ROI style scoring
- Prometheus metrics
- Grafana dashboard
- Phoenix trace evidence
- SQLite outcome store and basic learning feedback loop

## Important Constraints
- Keep this lightweight and runnable using Docker Compose.
- Do not implement Kafka, NATS, Loki, Mimir, S3, full auth, Jira, ServiceNow, or enterprise chargeback in MVP.
- Mention enterprise features only in README roadmap.
- Default LLM mode should be mock/simulated so demo works without paid API keys.
- Optional Ollama support can be added, but must not be required.
- Do not store secrets or PII in logs, metrics, traces, or SQLite.

## Run
docker compose up --build

## Test
pytest

## Coding Style
- Python 3.11+
- FastAPI
- prometheus_client
- SQLite for local outcome store
- Clear modular files
- Keep functions small and testable
- Add docstrings for scoring and decision logic

## Verification Checklist
- /health works
- /generate works using mock LLM
- /metrics exposes Prometheus metrics
- Prometheus scrapes app
- Grafana loads dashboard
- Phoenix starts locally
- pytest passes
