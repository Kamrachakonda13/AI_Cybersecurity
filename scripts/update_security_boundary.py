#!/usr/bin/env python3
"""Rewrite the old security-boundary strings in docs/tools/*.md.

Replaces every known old boundary variant with the new tiered
"Governed security operations" text.

Dry-run by default. Pass --apply to write changes.

Usage:
    python scripts/update_security_boundary.py            # preview
    python scripts/update_security_boundary.py --apply    # write changes
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs" / "tools"

# Every old boundary string we observed across the 576 affected docs
# plus the sudo_arsenal.py default.
OLD_STRINGS = [
    "Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.",
    "Defensive/authorized testing only; no credential theft, payload delivery, persistence, C2, evasion or hack-back instructions.",
    "Educational and defensive guidance only. VEYRA does not provide hack-back, unrestricted credential attacks, payload deployment, persistence, C2, evasion or disruptive instructions.",
    "No payload delivery, persistence, C2, evasion, credential theft or hack-back instructions.",
]

NEW_TEXT = (
    "Governed security operations. VEYRA enables authorized security testing, "
    "red-team, blue-team, and defensive work on owned or explicitly permitted targets. "
    "Tools are tiered by risk: Standard (discovery, analysis, defensive verification), "
    "Privileged (high-impact testing requires privileged_admin and an approved engagement), "
    "and Isolated Lab Only (attack-capable tools may only run against lab/sandbox targets). "
    "All executions are scope-bound, evidence-captured, and audited. "
    "Out-of-scope activity, unowned targets, and unauthorized use are prohibited."
)


def replace_all(text: str) -> tuple[str, int]:
    count = 0
    for old in OLD_STRINGS:
        occurrences = text.count(old)
        if occurrences:
            text = text.replace(old, NEW_TEXT)
            count += occurrences
    return text, count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Write changes (default is dry-run)")
    args = ap.parse_args()

    total_files = 0
    total_replacements = 0
    for p in sorted(DOCS.glob("*.md")):
        try:
            original = p.read_text(encoding="utf-8")
        except Exception:
            continue
        new, n = replace_all(original)
        if n == 0:
            continue
        total_files += 1
        total_replacements += n
        if args.apply:
            p.write_text(new, encoding="utf-8")

    print(f"Mode:            {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Files affected:  {total_files}")
    print(f"Replacements:    {total_replacements}")
    if not args.apply:
        print()
        print("This was a DRY-RUN. No files were modified.")
        print("Re-run with --apply to write changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
