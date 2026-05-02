"""SQLite outcome store and simple feedback loop."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from app.config import get_settings
from app.models import OutcomeRecord


def _connect() -> sqlite3.Connection:
    db_path = Path(get_settings().database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the local outcome database used by the MVP feedback loop."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                prompt_hash TEXT NOT NULL,
                team TEXT NOT NULL,
                endpoint_name TEXT NOT NULL,
                user_tier TEXT NOT NULL,
                sla_tier TEXT NOT NULL,
                model TEXT NOT NULL,
                action TEXT NOT NULL,
                complexity_score INTEGER NOT NULL,
                risk_score INTEGER NOT NULL,
                business_value_score INTEGER NOT NULL,
                historical_failure_score INTEGER NOT NULL,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                latency_ms INTEGER NOT NULL,
                estimated_cost REAL NOT NULL,
                quality_score REAL NOT NULL,
                value_score REAL NOT NULL,
                prompt_roi_score REAL NOT NULL,
                success INTEGER NOT NULL,
                reason_codes TEXT NOT NULL,
                attribution_tags TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_endpoint_hash ON outcomes(endpoint_name, prompt_hash)")


def save_outcome(record: OutcomeRecord) -> str:
    init_db()
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO outcomes (
                request_id, prompt_hash, team, endpoint_name, user_tier, sla_tier,
                model, action, complexity_score, risk_score, business_value_score,
                historical_failure_score, prompt_tokens, completion_tokens, total_tokens,
                latency_ms, estimated_cost, quality_score, value_score, prompt_roi_score,
                success, reason_codes, attribution_tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.request_id,
                record.prompt_hash,
                record.team,
                record.endpoint_name,
                record.user_tier,
                record.sla_tier,
                record.model,
                record.action,
                record.complexity_score,
                record.risk_score,
                record.business_value_score,
                record.historical_failure_score,
                record.prompt_tokens,
                record.completion_tokens,
                record.total_tokens,
                record.latency_ms,
                record.estimated_cost,
                record.quality_score,
                record.value_score,
                record.prompt_roi_score,
                int(record.success),
                json.dumps(record.reason_codes),
                json.dumps(record.attribution_tags),
            ),
        )
        return str(cursor.lastrowid)


def get_historical_failure_score(endpoint_name: str, prompt_hash: str) -> int:
    """Return a 0-100 failure signal from previous matching outcomes."""
    init_db()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN success = 0 OR quality_score < 0.55 THEN 1 ELSE 0 END) AS failures
            FROM outcomes
            WHERE endpoint_name = ? AND prompt_hash = ?
            """,
            (endpoint_name, prompt_hash),
        ).fetchone()
    total = int(row["total"] or 0)
    if total == 0:
        return 0
    failures = int(row["failures"] or 0)
    return min(100, round((failures / total) * 100))


def get_prompt_seen_count(endpoint_name: str, prompt_hash: str) -> int:
    """Return previous outcome count for the same endpoint and prompt hash."""
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total FROM outcomes WHERE endpoint_name = ? AND prompt_hash = ?",
            (endpoint_name, prompt_hash),
        ).fetchone()
    return int(row["total"] or 0)


def _group_sum(field: str) -> dict[str, float]:
    with _connect() as conn:
        rows = conn.execute(f"SELECT {field} AS key, SUM(estimated_cost) AS value FROM outcomes GROUP BY {field}").fetchall()
    return {row["key"]: round(float(row["value"] or 0), 6) for row in rows}


def _group_count(field: str) -> dict[str, int]:
    with _connect() as conn:
        rows = conn.execute(f"SELECT {field} AS key, COUNT(*) AS value FROM outcomes GROUP BY {field}").fetchall()
    return {row["key"]: int(row["value"]) for row in rows}


def get_cost_by_team() -> dict[str, float]:
    init_db()
    return _group_sum("team")


def get_decision_counts() -> dict[str, int]:
    init_db()
    return _group_count("action")


def get_summary() -> dict[str, Any]:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS total_requests,
                   AVG(quality_score) AS average_quality,
                   AVG(value_score) AS average_value_score,
                   SUM(estimated_cost) AS total_cost
            FROM outcomes
            """
        ).fetchone()
    return {
        "total_requests": int(row["total_requests"] or 0),
        "average_quality": round(float(row["average_quality"] or 0), 4),
        "average_value_score": round(float(row["average_value_score"] or 0), 4),
        "total_cost": round(float(row["total_cost"] or 0), 6),
        "cost_by_team": get_cost_by_team(),
        "decision_action_counts": get_decision_counts(),
        "model_usage_counts": _group_count("model"),
    }


def placeholder_calibration_job() -> dict[str, str]:
    """Placeholder for future calibration using accumulated outcomes."""
    return {"status": "skipped", "reason": "MVP uses inline historical failure scoring"}
