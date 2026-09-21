#!/usr/bin/env python3
"""Validate that every registered tool has a complete doc page.

Exit codes:
    0  all registered tools have complete docs
    1  missing or incomplete docs found
    2  registry import failed
"""
from pathlib import Path
import sys

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


def tool_id(t: dict) -> str:
    tid = t.get("id") or t.get("tool_id") or t.get("name", "")
    return tid.lower().replace(" ", "-").replace("/", "-")


def doc_path(tid: str) -> Path:
    return DOCS_DIR / f"{tid}.md"


def main() -> int:
    seen: dict[str, dict] = {}
    for t in extended_registry() + ai_cut() + ai_ecosys():
        tid = tool_id(t)
        if not tid:
            continue
        seen.setdefault(tid, t)

    missing: list[str] = []
    incomplete: list[tuple[str, list[str]]] = []

    for tid in sorted(seen):
        p = doc_path(tid)
        if not p.exists():
            missing.append(tid)
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        absent = [s for s in REQUIRED_SECTIONS if s not in text]
        if absent:
            incomplete.append((tid, absent))

    complete = len(seen) - len(missing) - len(incomplete)
    print(f"{len(seen)} registered")
    print(f"{complete} complete")
    print(f"{len(missing)} missing")
    print(f"{len(incomplete)} incomplete")

    if missing:
        print("\nMISSING:")
        for tid in missing[:50]:
            print(f"  - {tid}")
        if len(missing) > 50:
            print(f"  ... and {len(missing) - 50} more")

    if incomplete:
        print("\nINCOMPLETE:")
        for tid, absent in incomplete[:50]:
            print(f"  - {tid}")
            for s in absent:
                print(f"      missing: {s}")
        if len(incomplete) > 50:
            print(f"  ... and {len(incomplete) - 50} more")

    # Orphan detection: docs that exist but aren't in the registry.
    registered = set(seen.keys())
    orphans: list[str] = []
    if DOCS_DIR.exists():
        for p in DOCS_DIR.glob("*.md"):
            stem = p.stem.lower()
            if stem not in registered and stem not in {"readme", "index"}:
                orphans.append(stem)
    if orphans:
        print(f"\nORPHAN DOCS ({len(orphans)}) — on disk but not registered:")
        for o in sorted(orphans)[:50]:
            print(f"  - {o}")
        if len(orphans) > 50:
            print(f"  ... and {len(orphans) - 50} more")

    return 0 if not (missing or incomplete) else 1


if __name__ == "__main__":
    raise SystemExit(main())
