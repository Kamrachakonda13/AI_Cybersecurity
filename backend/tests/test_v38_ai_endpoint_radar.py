"""Tests for backend/app/services/v38_ai_endpoint_radar.py.

Tiny module — re-exports two constants from v38_posture_time_machine
plus a single overview() function.
"""
from app.services import v38_ai_endpoint_radar as radar
from app.services.v38_posture_time_machine import AI_PROVIDER_RADAR, ENDPOINT_RELEASES


def test_overview_returns_expected_keys():
    result = radar.overview()
    assert set(result.keys()) == {
        "release", "providers", "endpoint_platforms", "guardrails"}


def test_overview_release_is_3_8():
    assert radar.overview()["release"] == "3.8"


def test_overview_providers_match_source():
    assert radar.overview()["providers"] == AI_PROVIDER_RADAR


def test_overview_endpoints_match_source():
    assert radar.overview()["endpoint_platforms"] == ENDPOINT_RELEASES


def test_overview_guardrails_present():
    guardrails = radar.overview()["guardrails"]
    assert isinstance(guardrails, list)
    assert len(guardrails) >= 2
    joined = " ".join(guardrails).lower()
    assert "vulnerability" in joined
    assert "evidence" in joined or "telemetry" in joined


def test_module_does_not_execute_shell():
    """Structural: no subprocess imports."""
    from pathlib import Path
    import re
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "backend" / "app" / "services" /
           "v38_ai_endpoint_radar.py").read_text(encoding="utf-8")
    assert "subprocess" not in src
    assert not re.search(r"\bos\.system\b", src)
