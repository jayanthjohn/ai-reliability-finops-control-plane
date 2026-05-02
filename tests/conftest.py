import os

import pytest


@pytest.fixture(autouse=True)
def isolated_outcome_db(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTCOME_DB_PATH", str(tmp_path / "outcomes.db"))

