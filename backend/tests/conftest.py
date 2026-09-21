"""Prevent module-level collector-token settings from leaking across tests."""
import pytest
from app import db as dbmod


@pytest.fixture(autouse=True)
def isolate_collector_token(monkeypatch):
    monkeypatch.delenv("COLLECTOR_TOKEN", raising=False)
    yield


@pytest.fixture(autouse=True)
def restore_sessionlocal():
    """Snapshot and restore app.db.SessionLocal around every test.

    Prevents any test that monkey-patches the global SessionLocal
    (e.g. test_discovery) from leaking its throwaway engine into
    subsequent tests.
    """
    original = dbmod.SessionLocal
    yield
    dbmod.SessionLocal = original
