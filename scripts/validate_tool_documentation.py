#!/usr/bin/env python3
"""Validate that every registered tool has a complete doc page.

Checks:
    1. Every registered tool has a doc file
    2. Every doc contains the required section headings
    3. Every doc's header block matches the catalog values
       (Category, Purpose, VEYRA access, Execution boundary)
    4. Every doc's section content matches the catalog's help dict
       (What is it?, Safe workflow, Evidence to collect,
        Remediation and verification, Common mistakes, Security boundary)

Exit codes:
    0  all registered tools have complete, consistent docs
    1  missing docs, incomplete docs, or value drift found
    2  registry import failed
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

try:
    from app.services.extended_catalog import extended_registry
    from app.services.ai_cutting_edge_2026 import registry as ai_cut
    from app.services.ai_ecosystem import registry as ai_ecosys
except Exception as exc:
    print(f"FATAL: could not import tool registries: {exc}", file=sys.stderr)
    raise SystemExit(2)


REQUIRED_SECTIONS = [
    "## What is it?",
    "## Why VEYRA includes it",
    "## When should the team use it?",
    "## VEYRA UI workflow",
    "## Terminal starting point",
    "## Safe workflow",
    "## Evidence to collect",
    "## Remediation and verification",
    "## Common mistakes",
    "## Security boundary",
]

DOCS_DIR = REPO_ROOT / "docs" / "tools"

# Header lines like `**Category:** Network Defense  ` (2 trailing spaces for markdown)
FIELD_RE = {
    "category": re.compile(r"^\*\*Category:\*\*\s*(.+?)\s*$", re.MULTILINE),
    "purpose": re.compile(r"^\*\*Purpose:\*\*\s*(.+?)\s*$", re.MULTILINE),
    "access": re.compile(r"^\*\*VEYRA access:\*\*\s*(.+?)\s*$", re.MULTILINE),
    "boundary": re.compile(r"^\*\*Execution boundary:\*\*\s*(.+?)\s*$", re.MULTILINE),
}


def tool_id(t: dict) -> str:
    tid = t.get("id") or t.get("tool_id") or t.get("name", "")
    return tid.lower().replace(" ", "-").replace("/", "-")


def doc_path(tid: str) -> Path:
    return DOCS_DIR / f"{tid}.md"


def _norm(s: str) -> str:
    """Normalize a string for comparison (collapse whitespace, strip)."""
    return re.sub(r"\s+", " ", (s or "")).strip()


def _extract_section(text: str, heading: str, next_heading: str | None) -> str:
    """Extract the content between `heading` and the next heading (or EOF)."""
    pattern = re.escape(heading)
    m = re.search(pattern, text)
    if not m:
        return ""
    start = m.end()
    if next_heading:
        m2 = re.search(re.escape(next_heading), text[start:])
        if m2:
            return text[start: start + m2.start()]
    else:
        # Find next `## ` heading
        m2 = re.search(r"^##\s", text[start:], re.MULTILINE)
        if m2:
            return text[start: start + m2.start()]
    return text[start:]


def _section_paragraph(text: str, heading: str, next_heading: str | None) -> str:
    """Extract a section and collapse it to a single normalized line."""
    raw = _extract_section(text, heading, next_heading)
    # Drop markdown code fences so we compare only prose
    raw = re.sub(r"```.*?```", "", raw, flags=re.DOTALL)
    return _norm(raw)


def _section_list_items(text: str, heading: str, next_heading: str | None) -> list[str]:
    """Extract a section and return its `- item` bullet points (normalized)."""
    raw = _extract_section(text, heading, next_heading)
    items = []
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("- "):
            items.append(_norm(line[2:]))
    return items


SECTION_ORDER = [
    ("## What is it?", "## Why VEYRA includes it"),
    ("## Why VEYRA includes it", "## When should the team use it?"),
    ("## When should the team use it?", "## VEYRA UI workflow"),
    ("## VEYRA UI workflow", "## Terminal starting point"),
    ("## Terminal starting point", "## Safe workflow"),
    ("## Safe workflow", "## Evidence to collect"),
    ("## Evidence to collect", "## How to interpret results"),
    ("## How to interpret results", "## Remediation and verification"),
    ("## Remediation and verification", "## Common mistakes"),
    ("## Common mistakes", "## Team teaching summary"),
    ("## Team teaching summary", "## Security boundary"),
    ("## Security boundary", None),
]


def main() -> int:
    seen: dict[str, dict] = {}
    for t in extended_registry() + ai_cut() + ai_ecosys():
        tid = tool_id(t)
        if not tid:
            continue
        seen.setdefault(tid, t)

    missing: list[str] = []
    incomplete: list[tuple[str, list[str]]] = []
    drift: list[tuple[str, list[str]]] = []

    for tid in sorted(seen):
        tool = seen[tid]
        p = doc_path(tid)
        if not p.exists():
            missing.append(tid)
            continue

        text = p.read_text(encoding="utf-8", errors="ignore")
        absent = [s for s in REQUIRED_SECTIONS if s not in text]
        if absent:
            incomplete.append((tid, absent))
            continue

        # --- Field-level value checks ---
        problems: list[str] = []

        # Header block fields
        h = tool.get("help", {}) or {}
        expected_headers = {
            "category": _norm(str(tool.get("category", ""))),
            "purpose":  _norm(str(tool.get("purpose", ""))),
            "access":   _norm(str(tool.get("access_tier", ""))),
            "boundary": _norm(str(tool.get("execution_profile", ""))),
        }
        for key, pattern in FIELD_RE.items():
            m = pattern.search(text)
            if not m:
                problems.append(f"header/{key}: missing line in doc")
                continue
            actual = _norm(m.group(1))
            if actual != expected_headers[key]:
                problems.append(
                    f"header/{key}: doc={actual!r} catalog={expected_headers[key]!r}"
                )

        # Section content checks
        # `## What is it?` — equals help.summary (which is purpose)
        expected_summary = _norm(
            str(h.get("summary", tool.get("purpose", ""))))
        actual_summary = _section_paragraph(
            text, "## What is it?", "## Why VEYRA includes it")
        if actual_summary and actual_summary != expected_summary:
            problems.append(
                f"section/summary: doc={actual_summary[:60]!r} catalog={expected_summary[:60]!r}"
            )

        # `## Safe workflow`
        expected_sw = _norm(str(h.get("safe_workflow", "")))
        if expected_sw:
            actual_sw = _section_paragraph(
                text, "## Safe workflow", "## Evidence to collect")
            if actual_sw and actual_sw != expected_sw:
                problems.append(
                    f"section/safe_workflow: doc={actual_sw[:60]!r} catalog={expected_sw[:60]!r}"
                )

        # `## Evidence to collect` — list of bullets
        expected_ev = [_norm(x) for x in (h.get("expected_evidence") or [])]
        actual_ev = _section_list_items(
            text, "## Evidence to collect", "## How to interpret results"
        )
        if expected_ev and actual_ev and actual_ev != expected_ev:
            problems.append(
                f"section/evidence: doc={actual_ev!r} catalog={expected_ev!r}"
            )

        # `## Remediation and verification`
        expected_rv = _norm(str(h.get("next_step", "")))
        if expected_rv:
            actual_rv = _section_paragraph(
                text, "## Remediation and verification", "## Common mistakes"
            )
            if actual_rv and actual_rv != expected_rv:
                problems.append(
                    f"section/next_step: doc={actual_rv[:60]!r} catalog={expected_rv[:60]!r}"
                )

        # `## Common mistakes` — list of bullets
        expected_cm = [_norm(x) for x in (h.get("common_mistakes") or [])]
        actual_cm = _section_list_items(
            text, "## Common mistakes", "## Team teaching summary"
        )
        if expected_cm and actual_cm and actual_cm != expected_cm:
            problems.append(
                f"section/common_mistakes: doc={actual_cm!r} catalog={expected_cm!r}"
            )

        # `## Security boundary`
        expected_sb = _norm(str(h.get("help_boundary", "")))
        if expected_sb:
            actual_sb = _section_paragraph(text, "## Security boundary", None)
            if actual_sb and actual_sb != expected_sb:
                problems.append(
                    f"section/security_boundary: doc={actual_sb[:60]!r} catalog={expected_sb[:60]!r}"
                )

        if problems:
            drift.append((tid, problems))

    complete = len(seen) - len(missing) - len(incomplete) - len(drift)

    print(f"{len(seen)} registered")
    print(f"{complete} complete")
    print(f"{len(missing)} missing")
    print(f"{len(incomplete)} incomplete")
    print(f"{len(drift)} value-drift")

    if missing:
        print("\nMISSING:")
        for tid in missing[:20]:
            print(f"  - {tid}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")

    if incomplete:
        print("\nINCOMPLETE:")
        for tid, absent in incomplete[:20]:
            print(f"  - {tid}")
            for s in absent:
                print(f"      missing section: {s}")
        if len(incomplete) > 20:
            print(f"  ... and {len(incomplete) - 20} more")

    if drift:
        print("\nVALUE DRIFT:")
        for tid, problems in drift[:20]:
            print(f"  - {tid}")
            for prob in problems:
                print(f"      {prob}")
        if len(drift) > 20:
            print(f"  ... and {len(drift) - 20} more")

    # Orphan detection
    registered = set(seen.keys())
    orphans: list[str] = []
    if DOCS_DIR.exists():
        for p in DOCS_DIR.glob("*.md"):
            stem = p.stem.lower()
            if stem not in registered and stem not in {"readme", "index"}:
                orphans.append(stem)
    if orphans:
        print(f"\nORPHAN DOCS ({len(orphans)}):")
        for o in sorted(orphans)[:20]:
            print(f"  - {o}")
        if len(orphans) > 20:
            print(f"  ... and {len(orphans) - 20} more")

    return 0 if not (missing or incomplete or drift) else 1


if __name__ == "__main__":
    raise SystemExit(main())
