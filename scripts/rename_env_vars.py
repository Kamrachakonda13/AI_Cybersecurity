#!/usr/bin/env python3
"""Rename AEGISX_* environment variables to VEYRA_* in code and config.

Dry-run by default. Pass --apply to write changes.

Scans:
    *.py, *.jsx, *.js, *.ts, *.tsx, *.yml, *.yaml, *.env.example, Dockerfile

Only renames the PREFIX of env-var identifiers, e.g.:
    AEGISX_ADMIN_TOKEN  -> VEYRA_ADMIN_TOKEN
    AEGISX_SESSION_HOURS -> VEYRA_SESSION_HOURS

Does NOT touch AegisX/AEGISX as branding strings — that's a separate pass.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

EXTS = {".py", ".jsx", ".js", ".ts", ".tsx", ".yml",
        ".yaml", ".env", ".cfg", ".ini", ".md", ".json"}
EXTRA_NAMES = {".env.example", ".env.sample",
               "Dockerfile", "docker-compose.yml"}

SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    "dist", "build", "htmlcov", ".ruff_cache",
}

SKIP_FILES = {"rename_env_vars.py", "rebrand_aegisx_to_veyra.py"}

# Match the PREFIX only, in any of these contexts:
#   "AEGISX_"    (env-var literal)
#   'AEGISX_'
#   "AEGISX_ADMIN_TOKEN"
#   `AEGISX_ADMIN_TOKEN` (bash-style)
# The regex requires an uppercase identifier after the underscore.
# Match AEGISX_*, aegisx_*, and AegisX_* prefixes, all case variants.
# Group 1 captures the tail (e.g. "USER_TOKEN") so we can preserve or lower it.
ENV_RE = re.compile(r"\b(AEGISX|AegisX|aegisx)_([A-Za-z][A-Za-z0-9_]*)")


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


# Preserved identifiers — do not rename (persistence semantics)
PRESERVED_IDS = {"aegisx_pg"}


def rewrite(text: str) -> tuple[str, int]:
    # First, temporarily protect preserved IDs
    placeholders = {}
    for i, pid in enumerate(PRESERVED_IDS):
        token = f"__PRESERVED_{i}__"
        placeholders[token] = pid
        text = text.replace(pid, token)

    def _repl(m):
        prefix, tail = m.group(1), m.group(2)
        return f"VEYRA_{tail}"

    new, n = ENV_RE.subn(_repl, text)

    # Restore preserved IDs
    for token, pid in placeholders.items():
        new = new.replace(token, pid)
    return new, n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    total_files = 0
    total_replacements = 0
    changed: list[tuple[Path, int]] = []

    for p in iter_files():
        try:
            original = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError, OSError):
            continue
        new, n = rewrite(original)
        if n == 0:
            continue
        total_files += 1
        total_replacements += n
        changed.append((p.relative_to(REPO), n))
        if args.apply:
            p.write_text(new, encoding="utf-8")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"Mode:            {mode}")
    print(f"Files affected:  {total_files}")
    print(f"Replacements:    {total_replacements}")
    print()
    for rel, n in sorted(changed, key=lambda x: -x[1]):
        print(f"  {n:4d}  {rel}")
    if not args.apply:
        print("\nThis was a DRY-RUN. No files were modified.")
        print("Re-run with --apply to write changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
