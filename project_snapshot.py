"""
project_snapshot.py
Run from your project root:  python project_snapshot.py
Generates a single text file (project_snapshot.txt) you can paste back to me.
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

# ---------- CONFIG ----------
OUTPUT_FILE = "project_snapshot.txt"

# Directories to skip entirely
SKIP_DIRS = {
    ".git", ".svn", ".hg", "__pycache__", "node_modules",
    "venv", ".venv", "env", ".env", "dist", "build",
    ".idea", ".vscode", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "htmlcov", ".tox", "coverage", "site-packages",
}

# File extensions considered "code" (contents will be included)
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h",
    ".hpp", ".cs", ".go", ".rs", ".rb", ".php", ".sh", ".bash",
    ".ps1", ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg",
    ".html", ".css", ".sql", ".md", ".txt", ".env.example",
}

# Files whose contents we always include even without a code extension
ALWAYS_INCLUDE = {
    "README", "README.md", "requirements.txt", "setup.py", "pyproject.toml",
    "package.json", "Dockerfile", "docker-compose.yml", "Makefile",
    ".gitignore",
}

# ---------- SECRET REDACTION ----------
SECRET_PATTERNS = [
    "api_key", "apikey", "secret", "password", "passwd", "token",
    "private_key", "access_key", "client_secret", "authorization",
]


def redact_line(line: str) -> str:
    """Redact obvious secret-looking lines."""
    lower = line.lower()
    if any(p in lower for p in SECRET_PATTERNS) and "=" in line:
        key = line.split("=", 1)[0]
        return f"{key}= <REDACTED>\n"
    return line

# ---------- FILE TREE ----------


def build_tree(root: Path):
    tree_lines = []
    total_files = 0
    total_dirs = 0
    total_bytes = 0
    ext_counter = {}

    for dirpath, dirnames, filenames in os.walk(root):
        # filter skipped dirs in-place so os.walk doesn't descend
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        rel_dir = Path(dirpath).relative_to(root)
        depth = 0 if str(rel_dir) == "." else len(rel_dir.parts)
        indent = "    " * depth

        if str(rel_dir) != ".":
            tree_lines.append(f"{indent}{rel_dir.name}/")
            total_dirs += 1

        for f in filenames:
            fp = Path(dirpath) / f
            try:
                size = fp.stat().st_size
            except OSError:
                size = 0
            total_files += 1
            total_bytes += size
            ext = fp.suffix.lower() or "<no ext>"
            ext_counter[ext] = ext_counter.get(ext, 0) + 1
            tree_lines.append(f"{indent}    {f}  ({size} bytes)")

    return tree_lines, total_files, total_dirs, total_bytes, ext_counter

# ---------- FILE CONTENTS ----------


def read_file_safe(path: Path, max_bytes=200_000):
    try:
        if path.stat().st_size > max_bytes:
            return f"<skipped: file larger than {max_bytes} bytes>"
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = [redact_line(l) for l in fh.readlines()]
        return "".join(lines)
    except Exception as e:
        return f"<could not read: {e}>"


def collect_files(root: Path):
    """Return list of (relpath, content) for code/config files."""
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            fp = Path(dirpath) / f
            rel = fp.relative_to(root)
            ext = fp.suffix.lower()
            include = (
                ext in CODE_EXTENSIONS
                or f in ALWAYS_INCLUDE
                or f.startswith(".env.example")
            )
            if include:
                results.append((str(rel), read_file_safe(fp)))
    return results

# ---------- GIT INFO (optional) ----------


def git_info(root: Path):
    info = {}
    git_dir = root / ".git"
    if not git_dir.exists():
        return {"git": "not a git repository"}
    try:
        head = (git_dir / "HEAD").read_text().strip()
        info["HEAD"] = head
        info["branch"] = head.replace(
            "ref: refs/heads/", "") if head.startswith("ref:") else "detached"
    except Exception as e:
        info["error"] = str(e)
    return info

# ---------- MAIN ----------


def main():
    root = Path.cwd()
    print(f"[*] Scanning project: {root}")

    tree_lines, total_files, total_dirs, total_bytes, ext_counter = build_tree(
        root)
    files = collect_files(root)

    out = []
    out.append("=" * 70)
    out.append("PROJECT SNAPSHOT")
    out.append(f"Generated: {datetime.now().isoformat()}")
    out.append(f"Root: {root}")
    out.append(f"Python: {sys.version.split()[0]} on {sys.platform}")
    out.append("=" * 70)

    # Summary
    out.append("\n## SUMMARY")
    out.append(f"Total files : {total_files}")
    out.append(f"Total dirs  : {total_dirs}")
    out.append(
        f"Total size  : {total_bytes:,} bytes ({total_bytes/1024:.1f} KB)")
    out.append("\n### File types")
    for ext, count in sorted(ext_counter.items(), key=lambda x: -x[1]):
        out.append(f"  {ext:<15} {count}")

    # Git
    out.append("\n## GIT")
    for k, v in git_info(root).items():
        out.append(f"  {k}: {v}")

    # Tree
    out.append("\n## PROJECT TREE")
    out.append("(dirs shown with trailing /, files with size in bytes)")
    out.append("\n".join(tree_lines))

    # Files
    out.append("\n## FILE CONTENTS")
    out.append(f"({len(files)} files included)")
    for rel, content in files:
        out.append("\n" + "-" * 70)
        out.append(f"### FILE: {rel}")
        out.append("-" * 70)
        out.append(content.rstrip())

    text = "\n".join(out)
    Path(OUTPUT_FILE).write_text(text, encoding="utf-8")

    # also print to terminal for easy copy
    print(text)
    print(f"\n[+] Snapshot written to {OUTPUT_FILE}")
    print(f"[+] Size: {len(text):,} characters")


if __name__ == "__main__":
    main()
