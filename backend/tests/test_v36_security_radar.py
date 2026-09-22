"""Tests for backend/app/services/v36_security_radar.py.

Pure-data module: RECOMMENDATIONS list + overview() + recommendations().
"""
from app.services import v36_security_radar as radar


def test_recommendations_non_empty():
    assert isinstance(radar.RECOMMENDATIONS, list)
    assert len(radar.RECOMMENDATIONS) >= 10


def test_recommendation_entries_have_required_fields():
    required = {"id", "name", "kind", "maturity",
                "reason", "source", "maps_to"}
    for r in radar.RECOMMENDATIONS:
        assert required.issubset(set(r.keys())), r


def test_recommendation_ids_unique():
    ids = [r["id"] for r in radar.RECOMMENDATIONS]
    assert len(ids) == len(set(ids))


def test_recommendation_kinds_valid():
    valid = {"tool", "standard"}
    for r in radar.RECOMMENDATIONS:
        assert r["kind"] in valid, r


def test_recommendation_maturity_valid():
    valid = {"recommended", "experimental"}
    for r in radar.RECOMMENDATIONS:
        assert r["maturity"] in valid, r


def test_recommendation_maps_to_is_list_of_strings():
    for r in radar.RECOMMENDATIONS:
        assert isinstance(r["maps_to"], list)
        assert all(isinstance(x, str) for x in r["maps_to"])


def test_overview_shape():
    result = radar.overview()
    assert set(result.keys()) == {
        "release", "generated_at", "recommendations", "principle"}


def test_overview_release_is_3_6():
    assert radar.overview()["release"] == "3.6"


def test_overview_recommendations_match_constant():
    assert radar.overview()["recommendations"] is radar.RECOMMENDATIONS


def test_overview_principle_mentions_evidence():
    principle = radar.overview()["principle"].lower()
    assert "evidence" in principle
    assert "verified" in principle or "review" in principle


def test_recommendations_no_filters_returns_all():
    assert radar.recommendations() == radar.RECOMMENDATIONS


def test_recommendations_filter_by_maturity():
    for m in {"recommended", "experimental"}:
        rows = radar.recommendations(maturity=m)
        assert all(r["maturity"] == m for r in rows)
        assert len(rows) > 0


def test_recommendations_filter_by_kind():
    for k in {"tool", "standard"}:
        rows = radar.recommendations(kind=k)
        assert all(r["kind"] == k for r in rows)
        assert len(rows) > 0


def test_recommendations_combined_filter():
    rows = radar.recommendations(maturity="recommended", kind="tool")
    for r in rows:
        assert r["maturity"] == "recommended"
        assert r["kind"] == "tool"


def test_recommendations_unknown_filter_empty():
    rows = radar.recommendations(maturity="__nonexistent__")
    assert rows == []


def test_module_does_not_execute_shell():
    from pathlib import Path
    import re
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "backend" / "app" / "services" /
           "v36_security_radar.py").read_text(encoding="utf-8")
    assert "subprocess" not in src
    assert not re.search(r"\bos\.system\b", src)
