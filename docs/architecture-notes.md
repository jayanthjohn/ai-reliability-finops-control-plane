# Architecture Notes

The MVP demonstrates pre-request decisioning before any LLM spend:

1. `/generate` receives request context.
2. Request Intelligence Classifier scores complexity, risk, business value, historical failure, and route recommendation.
3. Decision Engine selects the action and model path.
4. Mock LLM returns deterministic local output.
5. Quality and value scores are computed.
6. Outcome is stored in SQLite.
7. Prometheus metrics are updated.
8. Phoenix/OpenTelemetry tracing is attempted with a no-fail fallback.

The design keeps the decision boundary explicit: classification and routing happen before `llm_client` is invoked.

The SQLite feedback loop is intentionally simple. Historical failure uses previous outcomes for the same endpoint and prompt hash. A production calibration job could periodically re-weight route thresholds, model quality priors, and endpoint-specific policy.

