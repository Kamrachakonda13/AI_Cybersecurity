"""Tests for the checklist registry (pure data, no DB, no I/O).

Covers structural invariants only: uniqueness, required keys, enum
membership, and the deliberate gap between declared domains and
populated domains (governance / supply_chain / red_team / blue_team
are added in a later sub-commit).
"""
from __future__ import annotations

from collections import Counter

import pytest

from app.services.checklist_registry import (
    CADENCES,
    CHECKLISTS,
    DOMAINS,
    OWNER_ROLES,
    TIERS,
)

REQUIRED_KEYS = frozenset({
    "id",
    "domain",
    "category",
    "name",
    "purpose",
    "owner_role",
    "cadence",
    "scope",
    "tier",
    "evidence",
    "remediation",
    "status_chip_rule",
    "boundary",
})

CHIP_STATES = ("green", "amber", "yellow", "semi_red", "red")

# Expected snapshot for P6 (74 after network/cloud hardening). Bump when entries are added.
EXPECTED_COUNT = 74
EXPECTED_PER_DOMAIN = {
    "live_monitoring": 8,
    "identity": 6,
    "endpoint": 7,
    "network_defense": 9,
    "cloud_container": 10,
    "ai_agent": 6,
    "dfir": 5,
    "governance": 8,
    "supply_chain": 5,
    "red_team": 5,
    "blue_team": 5,
}


# ---------------------------------------------------------------------------
# Module-level invariants
# ---------------------------------------------------------------------------

def test_checklists_is_a_list_of_dicts():
    assert isinstance(CHECKLISTS, list)
    assert all(isinstance(c, dict) for c in CHECKLISTS)


def test_expected_total_count():
    assert len(CHECKLISTS) == EXPECTED_COUNT


def test_ids_are_unique():
    ids = [c["id"] for c in CHECKLISTS]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    assert not dupes, f"duplicate ids: {dupes}"


def test_ids_are_lowercase_hyphenated_slugs():
    for c in CHECKLISTS:
        slug = c["id"]
        assert slug == slug.lower(), slug
        assert " " not in slug, slug
        assert "_" not in slug, slug
        assert slug.strip("-") == slug, slug


# ---------------------------------------------------------------------------
# Per-entry schema
# ---------------------------------------------------------------------------

def test_every_entry_has_required_keys():
    for c in CHECKLISTS:
        missing = REQUIRED_KEYS - c.keys()
        assert not missing, f"{c['id']} missing keys: {sorted(missing)}"


def test_domain_is_declared():
    for c in CHECKLISTS:
        assert c["domain"] in DOMAINS, f"{c['id']} -> {c['domain']}"


def test_owner_role_is_valid():
    for c in CHECKLISTS:
        assert c["owner_role"] in OWNER_ROLES, f"{c['id']} -> {c['owner_role']}"


def test_cadence_is_valid():
    for c in CHECKLISTS:
        assert c["cadence"] in CADENCES, f"{c['id']} -> {c['cadence']}"


def test_tier_is_valid():
    for c in CHECKLISTS:
        assert c["tier"] in TIERS, f"{c['id']} -> {c['tier']}"


def test_evidence_is_nonempty_list_of_strings():
    for c in CHECKLISTS:
        ev = c["evidence"]
        assert isinstance(ev, list), c["id"]
        assert ev, f"{c['id']} has empty evidence"
        assert all(isinstance(e, str) and e for e in ev), c["id"]


def test_text_fields_are_nonempty_strings():
    text_fields = (
        "category",
        "name",
        "purpose",
        "scope",
        "remediation",
        "status_chip_rule",
        "boundary",
    )
    for c in CHECKLISTS:
        for field in text_fields:
            value = c[field]
            assert isinstance(value, str), f"{c['id']}.{field} not str"
            assert value.strip(), f"{c['id']}.{field} is blank"


# ---------------------------------------------------------------------------
# Status chip rule
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("state", CHIP_STATES)
def test_chip_states_are_documented(state):
    # semi_red may be unused in early domains; the set is still the vocabulary.
    assert state in CHIP_STATES


def test_every_rule_references_green_and_red():
    for c in CHECKLISTS:
        rule = c["status_chip_rule"]
        assert "green=" in rule, f"{c['id']} rule missing green"
        assert "red=" in rule, f"{c['id']} rule missing red"


def test_every_rule_uses_only_declared_chip_states():
    import re

    for c in CHECKLISTS:
        rule = c["status_chip_rule"]
        # Extract tokens like "green=", "amber=", "semi_red=" etc.
        used = set(re.findall(r"\b([a-z_]+)=", rule))
        unknown = used - set(CHIP_STATES)
        assert not unknown, f"{c['id']} uses unknown chip states: {unknown}"


# ---------------------------------------------------------------------------
# Domain coverage snapshot
# ---------------------------------------------------------------------------

def test_per_domain_counts_match_snapshot():
    actual = Counter(c["domain"] for c in CHECKLISTS)
    assert dict(actual) == EXPECTED_PER_DOMAIN


def test_all_declared_domains_are_populated():
    populated = {c["domain"] for c in CHECKLISTS}
    declared = set(DOMAINS)
    assert populated <= declared
    assert declared - populated == set(), (
        f"declared but unpopulated: {declared - populated}"
    )


def test_no_orphan_domains():
    for c in CHECKLISTS:
        assert c["domain"] in DOMAINS, f"{c['id']} has undeclared domain {c['domain']}"
