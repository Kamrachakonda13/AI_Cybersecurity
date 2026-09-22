"""Tests for backend/app/services/v40_verification_adapters.py.

This module defines the supply-chain verification adapter registry and a
read-only inventory function. It does NOT execute anything — that contract
is enforced structurally here (no subprocess, no download).
"""
import re
from pathlib import Path

from app.services import v40_verification_adapters as adapters


REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "backend" / "app" / \
    "services" / "v40_verification_adapters.py"

EXPECTED_ADAPTERS = {"tuf", "cosign", "syft", "grype"}


def test_adapter_registry_has_exactly_four_adapters():
    assert set(adapters.ADAPTERS.keys()) == EXPECTED_ADAPTERS


def test_each_adapter_has_purpose_and_binary():
    for name, spec in adapters.ADAPTERS.items():
        assert "purpose" in spec, f"{name} missing 'purpose'"
        assert "binary" in spec, f"{name} missing 'binary'"
        assert isinstance(spec["purpose"], str) and spec["purpose"], name
        assert isinstance(spec["binary"], str) and spec["binary"], name


def test_inventory_returns_all_adapters():
    inv = adapters.inventory()
    assert isinstance(inv, list)
    assert len(inv) == len(adapters.ADAPTERS)
    names = {entry["adapter"] for entry in inv}
    assert names == EXPECTED_ADAPTERS


def test_inventory_entries_have_required_fields():
    for entry in adapters.inventory():
        assert "adapter" in entry
        assert "purpose" in entry
        assert "binary" in entry
        assert "available_on_control_plane" in entry
        assert "execution" in entry


def test_inventory_availability_is_boolean():
    for entry in adapters.inventory():
        assert isinstance(entry["available_on_control_plane"], bool), entry


def test_inventory_execution_is_managed_worker_only():
    """Every adapter must be marked as running only on managed workers."""
    for entry in adapters.inventory():
        assert entry["execution"] == "managed verification worker only", entry


def test_inventory_is_deterministic():
    """Calling inventory() twice returns the same set of adapters."""
    a = {e["adapter"] for e in adapters.inventory()}
    b = {e["adapter"] for e in adapters.inventory()}
    assert a == b


def test_module_does_not_execute_anything_structurally():
    """Regression guard: the module must not import subprocess, os.system,
    or otherwise execute shell commands. The inventory() function uses
    shutil.which(), which is a lookup only — it does not execute."""
    source = MODULE_PATH.read_text(encoding="utf-8")

    # No subprocess execution
    assert "subprocess" not in source, "subprocess imported — module must not execute commands"
    # No os.system / os.popen
    assert not re.search(r"\bos\.system\b", source)
    assert not re.search(r"\bos\.popen\b", source)
    # shutil.which is the only allowed member of shutil
    assert "shutil.which" in source, "expected shutil.which for availability lookup"
    assert "shutil.os" not in source
