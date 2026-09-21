"""Prevent module-level collector-token settings from leaking across tests."""
import pytest

@pytest.fixture(autouse=True)
def isolate_collector_token(monkeypatch):
    monkeypatch.delenv("COLLECTOR_TOKEN", raising=False)
    yield
