"""Runtime configuration for the local demo."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class BudgetState:
    pressure: str = "normal"
    daily_budget_usd: float = 20.0


@dataclass(frozen=True)
class SloState:
    at_risk: bool = False
    target_latency_ms: int = 1500


@dataclass(frozen=True)
class Settings:
    service_name: str = "ai-control-plane"
    llm_mode: str = "mock"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.2:1b"
    database_path: str = "data/outcomes.db"
    phoenix_endpoint: str = "http://phoenix:6006/v1/traces"
    budget_state: BudgetState = BudgetState()
    slo_state: SloState = SloState()


def get_settings() -> Settings:
    pressure = os.getenv("BUDGET_PRESSURE", "normal").lower()
    slo_at_risk = os.getenv("SLO_AT_RISK", "false").lower() == "true"
    return Settings(
        llm_mode=os.getenv("LLM_MODE", "mock").lower(),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
        database_path=os.getenv("OUTCOME_DB_PATH", "data/outcomes.db"),
        phoenix_endpoint=os.getenv("PHOENIX_OTLP_ENDPOINT", "http://phoenix:6006/v1/traces"),
        budget_state=BudgetState(pressure=pressure),
        slo_state=SloState(at_risk=slo_at_risk),
    )
