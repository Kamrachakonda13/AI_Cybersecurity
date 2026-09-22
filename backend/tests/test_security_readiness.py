"""Tests for backend/app/services/security_readiness.py.

Covers: control domain registry, exercise library filtering, documentation
readiness computation, and the readiness overview.
"""
from app.services import security_readiness as sr


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_control_domains_has_expected_count():
    assert len(sr.CONTROL_DOMAINS) == 10


def test_control_domains_shape():
    for entry in sr.CONTROL_DOMAINS:
        assert isinstance(entry, tuple)
        assert len(entry) == 3
        d_id, name, description = entry
        assert d_id and isinstance(d_id, str)
        assert name and isinstance(name, str)
        assert description and isinstance(description, str)


def test_control_domains_ids_are_unique():
    ids = [d[0] for d in sr.CONTROL_DOMAINS]
    assert len(ids) == len(set(ids)), f"duplicate domain ids: {ids}"


def test_expected_domain_ids_present():
    expected = {
        "identity", "scope", "worker", "evidence",
        "ai-runtime", "ai-data", "supply-chain",
        "detection", "resilience", "documentation",
    }
    actual = {d[0] for d in sr.CONTROL_DOMAINS}
    assert expected.issubset(actual), f"missing: {expected - actual}"


def test_exercises_have_required_fields():
    for ex in sr.EXERCISES:
        assert "id" in ex
        assert "name" in ex
        assert "track" in ex
        assert "goal" in ex
        assert "evidence" in ex
        assert isinstance(ex["evidence"], list)
        assert all(isinstance(e, str) for e in ex["evidence"])


def test_exercise_ids_are_unique():
    ids = [ex["id"] for ex in sr.EXERCISES]
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# exercise_library()
# ---------------------------------------------------------------------------

def test_exercise_library_returns_all_by_default():
    result = sr.exercise_library()
    assert result["track"] == "all"
    assert len(result["exercises"]) == len(sr.EXERCISES)


def test_exercise_library_filters_by_track():
    """Pick the first track from EXERCISES and verify filtering works."""
    if not sr.EXERCISES:
        return  # nothing to test
    track = sr.EXERCISES[0]["track"]
    result = sr.exercise_library(track=track)
    assert result["track"] == track
    for ex in result["exercises"]:
        assert ex["track"] == track


def test_exercise_library_unknown_track_returns_empty():
    result = sr.exercise_library(track="__nonexistent_track__")
    assert result["track"] == "__nonexistent_track__"
    assert result["exercises"] == []


# ---------------------------------------------------------------------------
# documentation_readiness()
# ---------------------------------------------------------------------------

def test_documentation_readiness_returns_expected_keys():
    result = sr.documentation_readiness()
    assert set(result.keys()) == {
        "registered_tools", "documented_tools", "missing_tools", "coverage_percent"
    }


def test_documentation_readiness_types():
    result = sr.documentation_readiness()
    assert isinstance(result["registered_tools"], int)
    assert isinstance(result["documented_tools"], int)
    assert isinstance(result["missing_tools"], list)
    assert isinstance(result["coverage_percent"], (int, float))


def test_documentation_readiness_counts_are_consistent():
    """documented + missing should equal registered."""
    result = sr.documentation_readiness()
    total = result["registered_tools"]
    documented = result["documented_tools"]
    missing = len(result["missing_tools"])
    assert documented + missing == total, (
        f"{documented} + {missing} != {total}"
    )


def test_documentation_readiness_coverage_in_range():
    result = sr.documentation_readiness()
    assert 0 <= result["coverage_percent"] <= 100


def test_documentation_readiness_high_coverage():
    """VEYRA currently has 587/587 docs complete. Coverage should be >= 99%."""
    result = sr.documentation_readiness()
    assert result["coverage_percent"] >= 99.0, (
        f"doc coverage dropped: {result['coverage_percent']}%"
    )


# ---------------------------------------------------------------------------
# readiness_overview()
# ---------------------------------------------------------------------------

def test_readiness_overview_returns_expected_keys():
    result = sr.readiness_overview()
    assert set(result.keys()) == {
        "release", "domains", "documentation", "exercise_count", "execution_boundary"
    }


def test_readiness_overview_release_is_3_3():
    assert sr.readiness_overview()["release"] == "3.3"


def test_readiness_overview_domains_match_control_domains():
    result = sr.readiness_overview()
    assert len(result["domains"]) == len(sr.CONTROL_DOMAINS)
    for domain in result["domains"]:
        assert set(domain.keys()) == {"id", "name", "description"}


def test_readiness_overview_exercise_count():
    result = sr.readiness_overview()
    assert result["exercise_count"] == len(sr.EXERCISES)


def test_readiness_overview_has_execution_boundary():
    """The boundary must explicitly mention no arbitrary commands / no hack-back."""
    boundary = sr.readiness_overview()["execution_boundary"]
    assert isinstance(boundary, str)
    assert "governed" in boundary.lower()
    assert "hack-back" in boundary.lower() or "hack_back" in boundary.lower()


def test_readiness_overview_nested_documentation():
    """The 'documentation' field must be the same shape as documentation_readiness()."""
    result = sr.readiness_overview()["documentation"]
    assert set(result.keys()) == {
        "registered_tools", "documented_tools", "missing_tools", "coverage_percent"
    }
