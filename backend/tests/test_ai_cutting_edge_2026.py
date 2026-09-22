"""Tests for backend/app/services/ai_cutting_edge_2026.py.

Pure-data AI tool registry — no execution, metadata only.
"""
import re
from pathlib import Path

from app.services import ai_cutting_edge_2026 as ace


REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "backend" / "app" / "services" / "ai_cutting_edge_2026.py"


def test_registry_constant_is_list():
    assert isinstance(ace.AI_CUTTING_EDGE_2026, list)
    assert len(ace.AI_CUTTING_EDGE_2026) >= 50


def test_registry_entries_are_5_tuples():
    for entry in ace.AI_CUTTING_EDGE_2026:
        assert isinstance(entry, tuple), entry
        assert len(entry) == 5, f"expected 5-tuple: {entry}"


def test_registry_entry_fields_nonempty():
    for tid, name, cat, purpose, worker in ace.AI_CUTTING_EDGE_2026:
        for val in (tid, name, cat, purpose, worker):
            assert isinstance(val, str) and val, f"empty field in {tid!r}"


def test_registry_ids_unique():
    ids = [e[0] for e in ace.AI_CUTTING_EDGE_2026]
    assert len(ids) == len(set(ids))


def test_registry_ids_are_slug_safe():
    slug_re = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    for tid, *_ in ace.AI_CUTTING_EDGE_2026:
        assert slug_re.match(tid), f"unsafe id: {tid!r}"


def test_registry_worker_profiles_valid():
    """execution_profile must be one of the approved patterns."""
    valid = {
        "approved_ai_worker",
        "isolated_lab_only",
        "isolated_analysis_worker",
        "approved_connector",
        "approved_worker",
        "experimental_worker",
        "experimental_connector",
    }
    for _tid, _name, _cat, _purpose, worker in ace.AI_CUTTING_EDGE_2026:
        assert worker in valid, f"unknown profile: {worker}"


def test_registry_function_returns_list():
    result = ace.registry()
    assert isinstance(result, list)
    assert len(result) == len(ace.AI_CUTTING_EDGE_2026)


def test_registry_entries_have_required_keys():
    required = {
        "id", "name", "category", "purpose", "execution_profile",
        "admin_only", "access_tier", "privileged_usage", "browser_shell",
        "status", "source", "help",
    }
    for entry in ace.registry():
        assert required.issubset(set(entry.keys())), entry["id"]


def test_registry_ids_unique_after_build():
    ids = [e["id"] for e in ace.registry()]
    assert len(ids) == len(set(ids))


def test_registry_ids_no_ampersand():
    """Regression: unsafe ids must not contain `&`."""
    for entry in ace.registry():
        assert "&" not in entry["id"], entry["id"]


def test_registry_help_subdict_has_expected_keys():
    expected = {
        "summary", "safe_workflow", "evidence", "common_mistakes",
        "next_step", "help_boundary",
    }
    for entry in ace.registry():
        assert expected.issubset(set(entry["help"].keys())), entry["id"]


def test_registry_boundary_uses_tier_language():
    """Post P1-4b, every boundary must use the new tier language."""
    for entry in ace.registry():
        boundary = entry["help"]["help_boundary"]
        assert "Governed security operations" in boundary
        assert "Standard" in boundary
        assert "Privileged" in boundary
        assert "Isolated Lab Only" in boundary


def test_registry_admin_only_always_true():
    for entry in ace.registry():
        assert entry["admin_only"] is True


def test_registry_browser_shell_always_false():
    for entry in ace.registry():
        assert entry["browser_shell"] is False


def test_registry_source_is_ai_cutting_edge():
    for entry in ace.registry():
        assert entry["source"] == "veyra-ai-cutting-edge-2026"


def test_registry_privileged_flag_derived_from_profile():
    """Entries on isolated_lab_only / isolated_analysis_worker are privileged."""
    privileged_profiles = {"isolated_lab_only", "isolated_analysis_worker"}
    for entry in ace.registry():
        expected = entry["execution_profile"] in privileged_profiles
        assert entry["privileged_usage"] == expected, entry["id"]


def test_registry_deterministic():
    a = [e["id"] for e in ace.registry()]
    b = [e["id"] for e in ace.registry()]
    assert a == b


def test_registry_known_entries_present():
    """Regression: key tools we know about are in the registry."""
    ids = {e["id"] for e in ace.registry()}
    for expected in ("pyrit", "deepteam", "giskard", "langsmith", "weave", "tuf"):
        assert expected in ids, f"missing known entry: {expected}"


def test_module_does_not_execute_shell():
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert not re.search(r"\bos\.system\b", source)
    assert not re.search(r"\bos\.popen\b", source)
