"""VEYRA state engine — status-chip computation (P6-C).

Chip colour = worst result in the run. Any critical/red item -> RED.

Mapping: green (0) < amber (1) < yellow (2) < semi_red (3) < red (4)
"""
from __future__ import annotations

CHIP_ORDER = ["green", "amber", "yellow", "semi_red", "red"]
CHIP_RANK = {c: i for i, c in enumerate(CHIP_ORDER)}

# result status -> chip
RESULT_TO_CHIP = {
    "pass": "green",
    "green": "green",
    "warn": "amber",
    "amber": "amber",
    "yellow": "yellow",
    "degraded": "yellow",
    "semi_red": "semi_red",
    "fail": "red",
    "red": "red",
    "critical": "red",
}


def chip_for_result(status: str) -> str:
    return RESULT_TO_CHIP.get(status.lower(), "amber")


def worst_chip(chips: list[str]) -> str:
    if not chips:
        return "green"
    return max(chips, key=lambda c: CHIP_RANK.get(c, 1))


def run_chip(results: list[dict]) -> str:
    """Worst chip across a list of {status} dicts."""
    chips = [chip_for_result(r.get("status", "pass")) for r in results]
    return worst_chip(chips)


def domain_chip(all_chips: list[str]) -> str:
    """Worst chip across a domain's checklist runs."""
    return worst_chip(all_chips)
