"""Tests for Wi-Fi/LAN discovery (`services/discovery.py` + 3 routes).

Help: OUI/vendor pure tests need no DB; upsert tests use shared in-memory
StaticPool SQLite; route test uses TestClient (see test_teams for why).
"""
import pytest
import app.models as _models  # noqa: tables registered
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.db import Base
from app.main import app
from app.services.discovery import vendor_for_mac, normalize_mac, upsert_discovery


def test_mac_normalize_and_oui():
    assert normalize_mac("aa-bb-cc-11-22-33") == "AA:BB:CC:11:22:33"
    assert normalize_mac("aabbcc112233") == "AA:BB:CC:11:22:33"
    assert normalize_mac("bad") == ""
    assert vendor_for_mac("3C:15:C2:11:22:33") == "Apple"
    assert vendor_for_mac("24:6F:28:AA:BB:CC") == "Espressif (ESP32)"
    assert vendor_for_mac("FF:FF:FF:00:00:00") == "Randomized (privacy MAC)"
    assert vendor_for_mac("FF:FF:FF:FF:FF:FF") == "Broadcast"
    assert vendor_for_mac("") == "Unknown"
    assert vendor_for_mac("DA:48:75:C5:80:92") == "Randomized (privacy MAC)"
    assert vendor_for_mac("56:DE:AE:1F:91:8C") == "Randomized (privacy MAC)"
    assert vendor_for_mac("98:BA:5F:F1:84:18") == "TP-Link"
    assert vendor_for_mac(
        "44:F7:9F:19:A6:1F") == "Cloud Network Tech (Foxconn OEM)"


def _db():
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    S = sessionmaker(bind=eng)
    Base.metadata.create_all(bind=eng)
    return S()


def test_upsert_matches_mac_then_updates():
    s = _db()
    out = upsert_discovery(s, [{"ip_address": "192.168.1.20", "mac": "3c:15:c2:aa:bb:cc",
                                "hostname": "iphone", "source": "agent-discover"}])
    assert out == {"hosts": 1, "new": 1}
    out = upsert_discovery(s, [{"ip_address": "192.168.1.99", "mac": "3C:15:C2:AA:BB:CC",
                                "hostname": "iphone-renamed", "source": "x"}])
    # same MAC → update, IP follows device
    assert out == {"hosts": 1, "new": 0}
    from app.models import DiscoveredHost
    row = s.query(DiscoveredHost).one()
    assert row.ip_address == "192.168.1.99" and row.vendor == "Apple"
    out = upsert_discovery(s, [{"ip_address": "192.168.1.99", "mac": "",
                                "hostname": "", "source": ""}])  # blanks don't wipe
    assert s.query(DiscoveredHost).one().hostname == "iphone-renamed"
    s.close()


@pytest.fixture
def client_with_fresh_db():
    """TestClient wired to a throwaway StaticPool SQLite DB.

    Restores app.db.SessionLocal on teardown so subsequent tests are
    not affected by this fixture's monkey-patching.
    """
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Testing = sessionmaker(bind=eng)
    assert hasattr(_models, "DiscoveredHost")
    Base.metadata.create_all(bind=eng)
    from app import db as dbmod
    original = dbmod.SessionLocal
    dbmod.SessionLocal = Testing
    try:
        yield TestClient(app)
    finally:
        dbmod.SessionLocal = original


def test_discovery_routes(client_with_fresh_db):
    c = client_with_fresh_db
    r = c.post("/api/ingest/discovery", json=[
        {"ip_address": "192.168.1.1", "mac": "B8:27:EB:00:11:22", "hostname": "pi-hole"},
        {"ip_address": "192.168.1.50", "mac": "", "hostname": ""}])
    assert r.json()["new"] == 2
    hosts = {h["ip_address"]: h for h in c.get("/api/discovery/hosts").json()}
    assert hosts["192.168.1.1"]["vendor"] == "Raspberry Pi"
    summ = c.get("/api/discovery/summary").json()
    assert summ["total"] == 2 and summ["by_vendor"]["Raspberry Pi"] == 1
