# AI Reliability, Quality & FinOps Control Plane

MVP for decision-driven LLM usage — optimizing cost, quality, and trust *before* execution and validating outcomes *after*.

---

## Why this exists

Most LLM systems answer:

- How good was the response?
- How much did it cost?

This project focuses on a more important question:

👉 *Was this the right decision for this request before we spent tokens?*

---

## What this does

Instead of directly calling an LLM, this control plane:

1. Classifies the request (complexity, risk, business value, historical signals)
2. Decides the optimal route (cheap / premium / review / cache)
3. Executes using an offline or mock model
4. Scores the outcome (quality, value, hallucination risk)
5. Provides full observability:
   - Metrics (cost, latency, usage trends)
   - Traces (input → decision → output → scoring)
   - UI explainability

---

## Key capabilities

- Pre-request decisioning (before LLM call)
- Dynamic routing based on request characteristics
- Offline LLM support (Ollama)
- Post-response validation including hallucination detection
- Trace-level explainability (Phoenix)
- Metrics-driven visibility (Grafana)
- Feedback-ready architecture (foundation for learning loop)

---

## Core idea

> Don’t just use AI.  
> **Decide how to use it before you spend — and validate it after.**

---

## Architecture Summary

Request flow:

1. User sends prompt via UI or API
2. `request_classifier` computes:
   - complexity_score
   - risk_score
   - business_value_score
   - historical_failures
3. `decision_engine` selects action:
   - cheap / balanced / premium
   - cache / review / block
4. `llm_client` executes:
   - mock mode OR
   - offline LLM (Ollama)
5. Scoring layer computes:
   - quality_score
   - value_score
   - prompt_roi_score
   - hallucination_score
6. `outcome_store` persists results
7. `metrics` exposes Prometheus metrics
8. `tracing` sends data to Phoenix

---

## Quick Start (Run in 5 minutes)

### Prerequisites

- Docker Desktop installed and running  
- (Optional) Ollama for offline LLM  

---

### 1. Clone the repo

```bash
git clone <your-repo-link>
cd ai-reliability-finops-control-plane
```

---

### 2. Start the system (default: mock LLM)

```bash
docker compose up --build
```

---

### 3. Open the UI

- Chat UI → http://localhost:8000  
- API Docs → http://localhost:8000/docs  
- Grafana → http://localhost:3000 (admin / admin)  
- Phoenix → http://localhost:6006  

---

### 4. Try control plane scenarios

Use built-in UI scenarios:

- Low Cost Route  
- High Value / Premium Route  
- Security Guardrail  
- Cache / Repeat Request  
- Hallucination Risk  

Each scenario demonstrates:
- request classification  
- routing decision  
- model execution  
- scoring + observability  

---

## Optional: Run with Offline LLM (Ollama)

### Install and start Ollama

```bash
brew install ollama
ollama pull llama3.2:1b
ollama serve
```

---

### Run system with Ollama

```bash
LLM_MODE=ollama docker compose up --build
```

---

### What changes in Ollama mode?

- Real LLM responses  
- Higher latency (expected)  
- Same decision, scoring, tracing, and metrics flow  

---

## UI Features

- Chat interface with scenario-driven testing  
- Decision Panel:
  - model selection  
  - routing decision  
  - classification scores  
- Metrics Panel:
  - tokens, latency, cost  
  - value score  
  - hallucination risk  
- Trace linking:
  - direct mapping to Phoenix traces  

---

## Observability

### Metrics (Grafana)

- Request volume  
- Token usage  
- Latency  
- Cost trends  
- Decision actions  
- Hallucination score  

---

### Tracing (Phoenix)

Each request captures:

- Input prompt  
- Output response  
- Model and routing decision  
- Tokens and cost  
- Quality and value scores  
- Hallucination risk  

---

## Demo Walkthrough (2 minutes)

1. Open UI → http://localhost:8000  
2. Select **Low Cost Route** → observe cheap routing  
3. Select **High Value / Premium Route** → observe routing change  
4. Select **Hallucination Risk**  
   - Model generates plausible response  
   - System flags **high hallucination risk 🔴**  
5. Open Phoenix → inspect trace  
6. Open Grafana → observe metrics  

---

## API

### Health

```bash
curl http://localhost:8000/health
```

---

### Generate

```bash
curl -s http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Summarize why a login API might return a 401 Unauthorized error in 3 bullet points.",
    "team": "platform",
    "endpoint_name": "support-assistant",
    "user_tier": "standard",
    "sla_tier": "standard",
    "environment": "demo"
  }'
```

---

## Tests

```bash
pytest
```

---

## Troubleshooting

- No Grafana data → send a few requests first  
- No Phoenix traces → fallback logging still works  
- Ports in use → update docker-compose.yml  
- Reset state → remove Docker volume  

---

## What is excluded (by design)

This MVP does NOT include:

- Kafka / NATS  
- Full auth / RBAC  
- Enterprise chargeback  
- External ticketing integrations  

👉 Focus is on **core decision + observability loop**

---

## Roadmap

- SLO-aware budget engine  
- Shadow routing / model benchmarking  
- Online LLM validation (judge model)  
- LLM resilience & chaos testing  

---

## Summary

This project demonstrates a simple but powerful idea:

👉 AI systems should not just respond — they should **decide, act, and learn**.
