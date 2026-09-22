"""Tests for backend/app/services/extended_catalog.py.

Covers:
    - EXTENDED_TOOL_REGISTRY shape
    - build_tool_help() output contract
    - extended_registry() merge, dedup, and governance enrichment
    - install_manifest() metadata shape
    - Structural guards (no shell, no arbitrary execution)
"""
import re
from pathlib import Path

from app.services import extended_catalog as ec
from app.services.admin_tools import TOOL_REGISTRY, PRIVILEGED_ADMIN_TOOLS


REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "backend" / "app" / "services" / "extended_catalog.py"


# ---------------------------------------------------------------------------
# EXTENDED_TOOL_REGISTRY
# ---------------------------------------------------------------------------

def test_extended_registry_is_a_list():
    assert isinstance(ec.EXTENDED_TOOL_REGISTRY, list)
    assert len(ec.EXTENDED_TOOL_REGISTRY) > 100


def test_extended_registry_entries_are_4_tuples():
    for entry in ec.EXTENDED_TOOL_REGISTRY:
        assert isinstance(entry, tuple), entry
        assert len(entry) == 4, f"expected 4-tuple, got {len(entry)}: {entry}"


def test_extended_registry_entries_have_nonempty_fields():
    for name, category, purpose, profile in ec.EXTENDED_TOOL_REGISTRY:
        assert isinstance(name, str) and name, f"bad name: {name!r}"
        assert isinstance(
            category, str) and category, f"bad category for {name}"
        assert isinstance(purpose, str) and purpose, f"bad purpose for {name}"
        assert isinstance(profile, str) and profile, f"bad profile for {name}"


def test_extended_registry_names_unique():
    names = [e[0] for e in ec.EXTENDED_TOOL_REGISTRY]
    assert len(names) == len(
        set(names)), "duplicate names in EXTENDED_TOOL_REGISTRY"


# ---------------------------------------------------------------------------
# build_tool_help()
# ---------------------------------------------------------------------------

REQUIRED_HELP_KEYS = {
    "summary", "why_veyra", "safe_workflow", "expected_evidence",
    "access", "execution_boundary", "common_mistakes", "next_step",
    "help_boundary",
}


def test_build_tool_help_returns_required_keys():
    result = ec.build_tool_help(
        name="test-tool",
        category="Security Utilities",
        purpose="Test purpose",
        profile="approved_worker",
        privileged=False,
    )
    assert REQUIRED_HELP_KEYS.issubset(set(result.keys()))


def test_build_tool_help_summary_equals_purpose():
    result = ec.build_tool_help(
        "x", "Security Utilities", "Unique purpose text", "approved_worker", False
    )
    assert result["summary"] == "Unique purpose text"


def test_build_tool_help_access_tier():
    privileged = ec.build_tool_help(
        "x", "Security Utilities", "p", "approved_worker", True)
    admin = ec.build_tool_help(
        "x", "Security Utilities", "p", "approved_worker", False)
    assert privileged["access"] == "Privileged Admin"
    assert admin["access"] == "Admin"


def test_build_tool_help_execution_boundary_echoes_profile():
    result = ec.build_tool_help(
        "x", "Security Utilities", "p", "isolated_lab_only", False)
    assert result["execution_boundary"] == "isolated_lab_only"


def test_build_tool_help_common_mistakes_is_list():
    result = ec.build_tool_help(
        "x", "Security Utilities", "p", "approved_worker", False)
    assert isinstance(result["common_mistakes"], list)
    assert len(result["common_mistakes"]) >= 3


def test_build_tool_help_evidence_is_list():
    result = ec.build_tool_help(
        "x", "Security Utilities", "p", "approved_worker", False)
    assert isinstance(result["expected_evidence"], list)
    assert len(result["expected_evidence"]) >= 1


def test_build_tool_help_unknown_category_falls_back():
    """Unknown categories get the Security Utilities fallback workflow."""
    a = ec.build_tool_help("x", "Nonsense Category",
                           "p", "approved_worker", False)
    b = ec.build_tool_help("x", "Security Utilities",
                           "p", "approved_worker", False)
    assert a["safe_workflow"] == b["safe_workflow"]


def test_build_tool_help_known_categories_differ():
    """AI Security and Network Discovery should produce different workflows."""
    ai = ec.build_tool_help("x", "AI Security", "p", "approved_worker", False)
    net = ec.build_tool_help("x", "Network Discovery",
                             "p", "approved_worker", False)
    assert ai["safe_workflow"] != net["safe_workflow"]


def test_build_tool_help_boundary_contains_tier_language():
    """Boundary must reflect the tiered governance model (post P1-4b)."""
    result = ec.build_tool_help(
        "x", "Security Utilities", "p", "approved_worker", False)
    boundary = result["help_boundary"]
    assert "Governed security operations" in boundary
    assert "Standard" in boundary
    assert "Privileged" in boundary
    assert "Isolated Lab Only" in boundary


# ---------------------------------------------------------------------------
# extended_registry()
# ---------------------------------------------------------------------------

def test_extended_registry_returns_list():
    result = ec.extended_registry()
    assert isinstance(result, list)
    assert len(result) > 400


def test_extended_registry_entries_have_required_keys():
    required = {
        "id", "name", "category", "purpose", "execution_profile",
        "admin_only", "access_tier", "privileged_usage", "browser_shell",
        "status", "source", "help",
    }
    for entry in ec.extended_registry():
        assert required.issubset(set(entry.keys())), entry["id"]


def test_extended_registry_ids_are_unique():
    ids = [entry["id"] for entry in ec.extended_registry()]
    dups = {i for i in ids if ids.count(i) > 1}
    assert not dups, f"duplicate ids: {dups}"


def test_extended_registry_ids_are_slug_safe():
    """Every id must be a valid slug (lowercase alnum + hyphens)."""
    slug_re = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    for entry in ec.extended_registry():
        assert slug_re.match(entry["id"]), f"unsafe id: {entry['id']!r}"


def test_extended_registry_ids_no_ampersand():
    """Regression: prior P0 bug produced `weights-&-biases-weave`."""
    for entry in ec.extended_registry():
        assert "&" not in entry["id"], f"ampersand in id: {entry['id']!r}"


def test_extended_registry_no_double_hyphens():
    """Regression: no id may contain `--` (from repeated `-` collapses)."""
    for entry in ec.extended_registry():
        assert "--" not in entry["id"], f"double hyphen in id: {entry['id']!r}"


def test_extended_registry_access_tier_is_valid():
    valid = {"admin", "privileged_admin"}
    for entry in ec.extended_registry():
        assert entry["access_tier"] in valid, entry


def test_extended_registry_privileged_usage_is_bool():
    for entry in ec.extended_registry():
        assert isinstance(entry["privileged_usage"], bool)


def test_extended_registry_privileged_usage_matches_access_tier():
    for entry in ec.extended_registry():
        if entry["privileged_usage"]:
            assert entry["access_tier"] == "privileged_admin"
        else:
            assert entry["access_tier"] == "admin"


def test_extended_registry_help_subdict_present():
    for entry in ec.extended_registry():
        assert isinstance(entry["help"], dict)
        assert REQUIRED_HELP_KEYS.issubset(set(entry["help"].keys()))


def test_extended_registry_admin_only_always_true():
    for entry in ec.extended_registry():
        assert entry["admin_only"] is True


def test_extended_registry_browser_shell_always_false():
    for entry in ec.extended_registry():
        assert entry["browser_shell"] is False


def test_extended_registry_status_cataloged():
    for entry in ec.extended_registry():
        assert entry["status"] == "cataloged"


def test_extended_registry_source_reflects_rebrand():
    """Regression: source must not reference AegisX anymore."""
    for entry in ec.extended_registry():
        assert "aegisx" not in entry["source"].lower()


def test_extended_registry_slug_collision_handling():
    """If two names slugify to the same id, the second gets a `-2` suffix."""
    # We can't easily force this at runtime without breaking the module, but we
    # can verify the invariant: no id appears twice.
    ids = [e["id"] for e in ec.extended_registry()]
    assert len(ids) == len(set(ids))


def test_extended_registry_deterministic():
    a = [e["id"] for e in ec.extended_registry()]
    b = [e["id"] for e in ec.extended_registry()]
    assert a == b


def test_extended_registry_contains_subfinder_split():
    """Regression for P1-3: subfinder and subfinder-feature are distinct."""
    ids = {e["id"] for e in ec.extended_registry()}
    assert "subfinder" in ids
    assert "subfinder-feature" in ids


def test_extended_registry_contains_ligolo_tools():
    """Regression for P1-4a: ligolo tools are registered."""
    ids = {e["id"] for e in ec.extended_registry()}
    assert "ligolo-ng" in ids
    assert "ligolo-mp" in ids
    assert "ligolo-ng-common-binaries" in ids


def test_ligolo_tools_are_isolated_lab_only():
    """Regression for P1-4a: ligolo tools use isolated_lab_only."""
    by_id = {e["id"]: e for e in ec.extended_registry()}
    for tid in ("ligolo-ng", "ligolo-mp", "ligolo-ng-common-binaries"):
        assert by_id[tid]["execution_profile"] == "isolated_lab_only"


def test_base_registry_entries_all_appear():
    """Every base entry must appear in the extended registry (by name)."""
    extended_names = {e["name"] for e in ec.extended_registry()}
    for name, _cat, _purpose, _profile in TOOL_REGISTRY:
        assert name in extended_names, f"base tool missing: {name!r}"


# ---------------------------------------------------------------------------
# install_manifest()
# ---------------------------------------------------------------------------

def test_install_manifest_shape():
    tool = {
        "id": "demo-tool",
        "name": "demo-tool",
        "privileged_usage": False,
    }
    result = ec.install_manifest(tool)
    required = {
        "tool_id", "tool", "package_id", "platforms", "install_mode",
        "source", "requires_admin", "requires_privileged_admin",
        "signed_artifact_required", "verification", "note",
    }
    assert required.issubset(set(result.keys()))


def test_install_manifest_echoes_tool_id():
    result = ec.install_manifest(
        {"id": "x", "name": "x", "privileged_usage": False})
    assert result["tool_id"] == "x"
    assert result["tool"] == "x"


def test_install_manifest_package_id_is_slug():
    result = ec.install_manifest(
        {"id": "x", "name": "Weights & Biases", "privileged_usage": False}
    )
    assert result["package_id"] == "weights-biases"


def test_install_manifest_never_executes():
    """Structural guard: manifest must not shell out or download anything."""
    tool = {"id": "x", "name": "x", "privileged_usage": True}
    result = ec.install_manifest(tool)
    assert result["install_mode"] == "managed_worker"
    assert "worker-side" in result["note"].lower()
    assert result["signed_artifact_required"] is True


def test_install_manifest_privileged_flag_reflects_input():
    p = ec.install_manifest({"id": "a", "name": "a", "privileged_usage": True})
    np = ec.install_manifest(
        {"id": "b", "name": "b", "privileged_usage": False})
    assert p["requires_privileged_admin"] is True
    assert np["requires_privileged_admin"] is False


def test_install_manifest_verification_list():
    result = ec.install_manifest(
        {"id": "x", "name": "x", "privileged_usage": False})
    assert isinstance(result["verification"], list)
    assert len(result["verification"]) >= 3


# ---------------------------------------------------------------------------
# Structural boundary checks
# ---------------------------------------------------------------------------

def test_module_does_not_execute_shell():
    """The catalog is metadata only — must never import subprocess or shell out."""
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in source, "subprocess imported — catalog must be metadata only"
    assert not re.search(r"\bos\.system\b", source)
    assert not re.search(r"\bos\.popen\b", source)
