#!/usr/bin/env python3
"""Add a 'historical snapshot' note to dated catalog files.

Dry-run by default. Pass --apply to write changes.
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"

# File -> version label
TARGETS = {
    "TOOL_HELP_CATALOG_V27.md": "v2.7",
    "TOOL_USAGE_CATALOG_V31.md": "v3.1",
    "TOOL_HELP_INDEX_V32.md": "v3.2",
    "TOOL_HELP_INDEX_V35.md": "v3.5",
    "TOOL_HELP_INDEX_V36.md": "v3.6",
}

MARKER = "> **Note:** This is a historical snapshot from VEYRA"


def build_note(version: str) -> str:
    return (
        f"> **Note:** This is a historical snapshot from VEYRA {version}. For current tool\n"
        f"> documentation, see [`docs/tools/`](tools/) — auto-generated from the catalog\n"
        f"> via `scripts/generate_tool_docs.py`.\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    for filename, version in TARGETS.items():
        p = DOCS / filename
        if not p.exists():
            print(f"SKIP (missing): {filename}")
            continue

        text = p.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"SKIP (already noted): {filename}")
            continue

        lines = text.splitlines(keepends=True)
        if not lines:
            print(f"SKIP (empty): {filename}")
            continue

        # Insert after the first line (H1)
        h1 = lines[0].rstrip("\n")
        note = build_note(version)
        new_text = h1 + "\n\n" + note + "\n" + "".join(lines[1:])

        if args.apply:
            p.write_text(new_text, encoding="utf-8")
            print(f"WROTE: {filename} (after H1: {h1!r})")
        else:
            print(f"WOULD WRITE: {filename}")
            print(f"  H1: {h1!r}")
            print(f"  + note: {note.splitlines()[0]}...")

    if not args.apply:
        print()
        print("This was a DRY-RUN. Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
