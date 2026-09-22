#!/usr/bin/env python3
"""Safely replace AegisX/AEGISX/aegisx with VEYRA/VEYRA/veyra across the repo.

Dry-run by default. Pass --apply to write changes.

Rules applied (in order, most specific first):
    AEGISX           -> VEYRA
    AegisX           -> VEYRA
    aegisx-extension -> veyra-extension
    aegisx_extension -> veyra_extension
    aegisx           -> veyra

Usage:
    python scripts/rebrand_aegisx_to_veyra.py            # dry-run
    python scripts/rebrand_aegisx_to_veyra.py --apply    # write changes
    python scripts/rebrand_aegisx_to_veyra.py --verbose  # show all files
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

EXTS = {
    ".py", ".md", ".json", ".yml", ".yaml",
    ".ts", ".tsx", ".js", ".jsx",
    ".txt", ".cfg", ".ini", ".toml", ".env",
}

EXTRA_NAMES = {".env.example", ".env.sample", "Dockerfile"}

SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    "dist", "build", "htmlcov", ".ruff_cache", ".tox",
}

# Files we never touch even if they match (historical context, migration notes)
SKIP_FILES = {
    "CHANGELOG.md",
    "MIGRATION.md",
    "HISTORY.md",
    "rebrand_aegisx_to_veyra.py",
    "rename_env_vars.py",
    "project_snapshot.txt",
}

RULES = [
    (re.compile(r"\bAEGISX\b"), "VEYRA"),
    (re.compile(r"\bAegisX\b"), "VEYRA"),
    (re.compile(r"\baegisx-extension\b"), "veyra-extension"),
    (re.compile(r"\baegisx_extension\b"), "veyra_extension"),
    (re.compile(r"\baegisx\b"), "veyra"),
]


def iter_files():
    for p in REPO.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        if p.suffix.lower() not in EXTS and p.name not in EXTRA_NAMES:
            continue
        yield p


def apply_rules(text: str) -> tuple[str, int]:
    count = 0
    for pattern, replacement in RULES:
        text, n = pattern.subn(replacement, text)
        count += n
    return text, count


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="Write changes (default is dry-run)")
    ap.add_argument("--verbose", action="store_true",
                    help="Show every changed file")
    args = ap.parse_args()

    total_files = 0
    total_replacements = 0
    changed_files: list[tuple[Path, int]] = []

    for p in iter_files():
        try:
            original = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError, OSError):
            continue
        new, n = apply_rules(original)
        if n == 0:
            continue
        total_files += 1
        total_replacements += n
        changed_files.append((p.relative_to(REPO), n))
        if args.apply:
            p.write_text(new, encoding="utf-8")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"Mode:            {mode}")
    print(f"Files affected:  {total_files}")
    print(f"Replacements:    {total_replacements}")
    print()

    limit = len(changed_files) if args.verbose else 40
    for rel, n in sorted(changed_files, key=lambda x: -x[1])[:limit]:
        print(f"  {n:4d}  {rel}")
    if len(changed_files) > limit:
        print(f"  ... and {len(changed_files) - limit} more")

    if not args.apply:
        print()
        print("This was a DRY-RUN. No files were modified.")
        print("Re-run with --apply to write changes.")
    else:
        print()
        print("Changes written. Review with: git diff --stat")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
