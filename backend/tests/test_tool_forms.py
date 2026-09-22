"""Tests for backend/app/services/tool_forms.py.

Covers the field-schema system (base fields, category/tool overrides) and
the contract-folding function that turns form params into (target, scope, params).
"""
import re
from pathlib import Path

import pytest

from app.services import tool_forms


REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "backend" / "app" / "services" / "tool_forms.py"


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

def test_environments_list():
    assert tool_forms.ENVIRONMENTS == ["lab", "approved_worker"]


def test_category_forms_is_non_empty_dict():
    assert isinstance(tool_forms.CATEGORY_FORMS, dict)
    assert len(tool_forms.CATEGORY_FORMS) >= 15


def test_tool_forms_is_dict():
    assert isinstance(tool_forms.TOOL_FORMS, dict)
    assert len(tool_forms.TOOL_FORMS) >= 5


def test_plan_only_note_is_string():
    assert isinstance(tool_forms.PLAN_ONLY_NOTE, str)
    assert "plan" in tool_forms.PLAN_ONLY_NOTE.lower()


# ---------------------------------------------------------------------------
# _base() — field construction
# ---------------------------------------------------------------------------

def test_base_has_required_fields():
    fields = tool_forms._base()
    names = {f["name"] for f in fields}
    assert {"target", "scope", "environment",
            "purpose", "approval_ticket"}.issubset(names)


def test_base_target_is_required_text():
    fields = tool_forms._base()
    target = next(f for f in fields if f["name"] == "target")
    assert target["required"] is True
    assert target["type"] == "text"


def test_base_scope_is_required_textarea():
    fields = tool_forms._base()
    scope = next(f for f in fields if f["name"] == "scope")
    assert scope["required"] is True
    assert scope["type"] == "textarea"


def test_base_environment_uses_environments_constant():
    fields = tool_forms._base()
    env = next(f for f in fields if f["name"] == "environment")
    assert env["type"] == "select"
    assert env["options"] == tool_forms.ENVIRONMENTS
    assert env["default"] == "lab"


def test_base_with_extra_fields():
    extra = [{"name": "custom", "label": "Custom",
              "type": "text", "required": False}]
    fields = tool_forms._base(extra)
    names = {f["name"] for f in fields}
    assert "custom" in names
    assert "target" in names  # base fields still present


def test_base_with_none_extra():
    fields = tool_forms._base(None)
    assert any(f["name"] == "target" for f in fields)


# ---------------------------------------------------------------------------
# PROFILE factory
# ---------------------------------------------------------------------------

def test_profile_lambda_returns_dict():
    p = tool_forms.PROFILE("Test Profile", ["a", "b"])
    assert isinstance(p, dict)
    assert p["name"] == "profile"
    assert p["label"] == "Test Profile"
    assert p["type"] == "select"
    assert p["options"] == ["a", "b"]
    assert p["default"] == "a"
    assert p["required"] is True


def test_profile_lambda_respects_default():
    p = tool_forms.PROFILE("Test", ["a", "b"], default="b")
    assert p["default"] == "b"


def test_profile_lambda_respects_help():
    p = tool_forms.PROFILE("Test", ["a"], help="my help text")
    assert p["help"] == "my help text"


# ---------------------------------------------------------------------------
# Field schema validation — all fields in all forms
# ---------------------------------------------------------------------------

def test_all_category_forms_have_valid_field_shapes():
    """Every field in every category form has the required keys."""
    for cat, fields in tool_forms.CATEGORY_FORMS.items():
        assert isinstance(fields, list), cat
        for f in fields:
            assert "name" in f, cat
            assert "label" in f, cat
            assert "type" in f, cat
            assert "required" in f, cat
            assert isinstance(f["name"], str) and f["name"], cat
            assert isinstance(f["required"], bool), cat


def test_all_tool_forms_have_valid_field_shapes():
    for name, fields in tool_forms.TOOL_FORMS.items():
        assert isinstance(fields, list), name
        for f in fields:
            assert "name" in f, name
            assert "label" in f, name
            assert "type" in f, name
            assert "required" in f, name


def test_all_category_forms_include_target():
    """Every category form must include the `target` field."""
    for cat, fields in tool_forms.CATEGORY_FORMS.items():
        names = {f["name"] for f in fields}
        assert "target" in names, f"missing target in {cat}"


def test_all_tool_forms_include_target():
    for name, fields in tool_forms.TOOL_FORMS.items():
        names = {f["name"] for f in fields}
        assert "target" in names, f"missing target in {name}"


# ---------------------------------------------------------------------------
# get_form()
# ---------------------------------------------------------------------------

def _tool(name="Nmap", category="Network Discovery", profile="approved_worker",
          access="admin", privileged=False):
    return {
        "id": name.lower().replace(" ", "-"),
        "name": name,
        "category": category,
        "purpose": "test",
        "execution_profile": profile,
        "access_tier": access,
        "privileged_usage": privileged,
    }


def test_get_form_returns_expected_keys():
    result = tool_forms.get_form(_tool())
    expected = {
        "tool_id", "tool", "category", "purpose", "execution_profile",
        "access_tier", "privileged_usage", "fields", "note",
    }
    assert set(result.keys()) == expected


def test_get_form_uses_tool_specific_form_when_available():
    nmap = tool_forms.get_form(
        _tool(name="Nmap", category="Network Discovery"))
    fields = nmap["fields"]
    names = {f["name"] for f in fields}
    # Nmap-specific field
    assert "timing" in names


def test_get_form_falls_back_to_category_form():
    """A tool without a specific form gets its category form."""
    tool = _tool(name="Some Unknown Tool", category="Network Discovery")
    result = tool_forms.get_form(tool)
    names = {f["name"] for f in result["fields"]}
    # Network Discovery category form has a `ports` field
    assert "ports" in names


def test_get_form_falls_back_to_base_for_unknown_category():
    tool = _tool(name="Some Unknown Tool", category="__Unknown Category__")
    result = tool_forms.get_form(tool)
    names = {f["name"] for f in result["fields"]}
    # Only base fields
    assert names == {"target", "scope",
                     "environment", "purpose", "approval_ticket"}


def test_get_form_echoes_tool_metadata():
    tool = _tool(name="Nmap", category="Network Discovery", profile="approved_worker",
                 access="admin", privileged=True)
    result = tool_forms.get_form(tool)
    assert result["tool"] == "Nmap"
    assert result["category"] == "Network Discovery"
    assert result["execution_profile"] == "approved_worker"
    assert result["access_tier"] == "admin"
    assert result["privileged_usage"] is True


def test_get_form_plan_only_note_for_connector():
    """Approved-connector tools get the plan-only note."""
    tool = _tool(name="Some Connector", category="AI Security",
                 profile="approved_connector")
    result = tool_forms.get_form(tool)
    assert result["note"] == tool_forms.PLAN_ONLY_NOTE


def test_get_form_no_note_for_normal_worker():
    tool = _tool(name="Nmap", category="Network Discovery",
                 profile="approved_worker")
    result = tool_forms.get_form(tool)
    assert result["note"] == ""


def test_get_form_handles_missing_optional_fields():
    """Empty tool dict should not crash — falls back to base."""
    result = tool_forms.get_form({})
    assert result["tool"] == ""
    assert "target" in {f["name"] for f in result["fields"]}


# ---------------------------------------------------------------------------
# build_contract_fields()
# ---------------------------------------------------------------------------

def test_build_contract_returns_3_tuple():
    tool = _tool(name="Nmap")
    target, scope, extra = tool_forms.build_contract_fields(tool, {
        "target": "10.10.20.17", "scope": "lab-web, 10.10.20.17",
        "environment": "lab", "purpose": "test",
    })
    assert target == "10.10.20.17"
    assert scope == ["lab-web", "10.10.20.17"]
    assert "environment" not in extra
    assert "purpose" not in extra
    assert "approval_ticket" not in extra


def test_build_contract_requires_target():
    with pytest.raises(ValueError, match="target is required"):
        tool_forms.build_contract_fields(_tool(name="Nmap"), {})


def test_build_contract_scope_defaults_to_target():
    target, scope, _ = tool_forms.build_contract_fields(
        _tool(name="Nmap"), {"target": "10.0.0.1"}
    )
    assert scope == ["10.0.0.1"]


def test_build_contract_scope_splits_on_comma():
    _, scope, _ = tool_forms.build_contract_fields(
        _tool(name="Nmap"), {"target": "t", "scope": "a, b, c"}
    )
    assert scope == ["a", "b", "c"]


def test_build_contract_scope_max_100():
    big_scope = ",".join(f"host-{i}" for i in range(101))
    with pytest.raises(ValueError, match="1..100"):
        tool_forms.build_contract_fields(
            _tool(name="Nmap"), {"target": "t", "scope": big_scope}
        )


def test_build_contract_scope_100_ok():
    big_scope = ",".join(f"host-{i}" for i in range(100))
    _, scope, _ = tool_forms.build_contract_fields(
        _tool(name="Nmap"), {"target": "t", "scope": big_scope}
    )
    assert len(scope) == 100


def test_build_contract_target_url_aliases_to_target():
    target, _, _ = tool_forms.build_contract_fields(
        _tool(name="Some Web Tool"), {"target_url": "http://x.test/"}
    )
    assert target == "http://x.test/"


def test_build_contract_artifact_aliases_to_target():
    target, _, _ = tool_forms.build_contract_fields(
        _tool(name="Some Container Tool"), {"artifact": "registry/org/app:1.4"}
    )
    assert target == "registry/org/app:1.4"


def test_build_contract_gateway_aliases_to_target():
    target, _, _ = tool_forms.build_contract_fields(
        _tool(name="Garak"), {"gateway": "http://lab-ai:4120"}
    )
    assert target == "http://lab-ai:4120"


def test_build_contract_extra_excludes_known_fields():
    _, _, extra = tool_forms.build_contract_fields(_tool(name="Nmap"), {
        "target": "t", "scope": "t", "environment": "lab",
        "purpose": "p", "approval_ticket": "CHG-1",
        "ports": "80,443",
    })
    assert extra == {"ports": "80,443"}


def test_build_contract_extra_excludes_empty_values():
    _, _, extra = tool_forms.build_contract_fields(_tool(name="Nmap"), {
        "target": "t", "ports": "  ", "profile": "",
    })
    assert extra == {}


def test_build_contract_metasploit_rejects_non_scanner_module():
    with pytest.raises(ValueError, match="auxiliary"):
        tool_forms.build_contract_fields(
            _tool(name="Metasploit Framework"),
            {"target": "t", "module": "exploit/multi/handler"},
        )


def test_build_contract_metasploit_accepts_scanner_module():
    tool = _tool(name="Metasploit Framework")
    target, _, extra = tool_forms.build_contract_fields(tool, {
        "target": "t", "module": "auxiliary/scanner/portscan/tcp",
    })
    assert target == "t"
    assert extra["module"] == "auxiliary/scanner/portscan/tcp"


def test_build_contract_handles_none_params():
    with pytest.raises(ValueError, match="target is required"):
        tool_forms.build_contract_fields(_tool(name="Nmap"), None)


# ---------------------------------------------------------------------------
# Structural guards
# ---------------------------------------------------------------------------

def test_module_does_not_execute_shell():
    """Structural: no subprocess / shell execution in tool_forms."""
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert not re.search(r"\bos\.system\b", source)
    assert not re.search(r"\bos\.popen\b", source)


def test_no_command_string_acceptance():
    """Any field that implies a raw command should not be text/textarea."""
    # Sample: check the entire CATEGORY_FORMS and TOOL_FORMS for any field
    # named "command" or "cmd" that would be a raw shell string
    forbidden_names = {"command", "cmd", "shell"}
    for source in (tool_forms.CATEGORY_FORMS, tool_forms.TOOL_FORMS):
        for _key, fields in source.items():
            for f in fields:
                assert f["name"] not in forbidden_names, (
                    f"raw shell field {f['name']!r} found"
                )
