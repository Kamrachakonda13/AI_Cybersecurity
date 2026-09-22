#!/usr/bin/env python3
"""Consolidate README.md: replace the top with a v5.0 header and remove
the duplicated v5.0 block at the bottom.

Dry-run by default. Pass --apply to write changes.
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
README = REPO / "README.md"
NEW_TOP_FILE = REPO / "scripts" / "_new_readme_top.md"

TOP_END_ANCHOR = "## v3.6 — Security Radar & Ecosystem Scout"
BOTTOM_DUPLICATE_ANCHOR = "\n# VEYRA v5.0 — Autonomous Security Control Plane\n"


def consolidate(text: str, new_top: str) -> str:
    if TOP_END_ANCHOR not in text:
        raise SystemExit(f"Could not find top anchor: {TOP_END_ANCHOR!r}")
    idx = text.index(TOP_END_ANCHOR)
    keep_region = text[idx:]

    if BOTTOM_DUPLICATE_ANCHOR in keep_region:
        dup_idx = keep_region.index(BOTTOM_DUPLICATE_ANCHOR)
        keep_region = keep_region[:dup_idx].rstrip() + "\n"

    return new_top.rstrip() + "\n\n" + keep_region


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if not NEW_TOP_FILE.exists():
        raise SystemExit(
            f"Expected markdown top at {NEW_TOP_FILE}. Create it first."
        )

    new_top = NEW_TOP_FILE.read_text(encoding="utf-8")
    original = README.read_text(encoding="utf-8")
    result = consolidate(original, new_top)

    print(f"Original size: {len(original):,} chars")
    print(f"New size:      {len(result):,} chars")
    print(f"Delta:         {len(result) - len(original):+,} chars")
    print()

    if not args.apply:
        print("DRY-RUN. To apply, run: python scripts/consolidate_readme.py --apply")
        return 0

    README.write_text(result, encoding="utf-8")
    print(f"Wrote {README}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
