#!/usr/bin/env python3
"""Generate per-tool markdown docs from the VEYRA catalog.

Reads the merged tool registry (extended_catalog + ai_cutting_edge_2026 +
ai_ecosystem) and renders one markdown file per tool to docs/tools/<id>.md.

Usage:
    python scripts/generate_tool_docs.py             # write docs (default)
    python scripts/generate_tool_docs.py --check     # dry-run; exit 1 if any differ
    python scripts/generate_tool_docs.py --verbose   # show every file written/changed

Exit codes:
    0  success (writes done, or --check found no drift)
    1  --check detected drift
    2  registry import failed
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs" / "tools"

# Make `app` importable when run from the repo root
sys.path.insert(0, str(REPO / "backend"))

try:
    from app.services.extended_catalog import extended_registry
    from app.services.ai_cutting_edge_2026 import registry as ai_cut
    from app.services.ai_ecosystem import registry as ai_ecosys
    from app.services.slug import slugify
except Exception as exc:
    print(f"FATAL: could not import registries: {exc}", file=sys.stderr)
    raise SystemExit(2)


# ---------------------------------------------------------------------------
# Static template strings — kept here so they are easy to audit and update
# ---------------------------------------------------------------------------

STATIC_WHY_VEYRA = (
    "Provides a governed, auditable entry point with role-based access, "
    "scope controls and normalized evidence."
)

STATIC_UI_WORKFLOW = [
    "1. Open **Tool Runner / Sudo Security Arsenal**.",
    "2. Search for **{name}** and read this guide before execution.",
    "3. Confirm the target/scope and business purpose.",
    "4. Confirm the user's entitlement and Sudo/approval requirements.",
    "5. Select the appropriate managed worker and execution profile.",
    "6. Run only the approved test; collect normalized evidence.",
    "7. Review results in the Security Graph/SOC where applicable.",
    "8. Remediate confirmed issues and schedule revalidation.",
]

STATIC_TERMINAL_INTRO = "Start with local discovery/help only on an enrolled worker:"

STATIC_TERMINAL_NOTES_1 = (
    "If the binary is not installed, use the VEYRA Tool Marketplace/install "
    "workflow rather than installing unapproved software manually. For "
    "SaaS/API-only capabilities, use the VEYRA connector/worker documented "
    "for that integration."
)

STATIC_TERMINAL_NOTES_2 = (
    "**Do not substitute arbitrary attack commands for the approved worker "
    "profile.** Tool-specific commands that can change security state require "
    "explicit authorization, scope and approval."
)

STATIC_INTERPRET = (
    "Treat tool output as a signal or measurement. Confirm affected assets, "
    "ownership, scope, timestamps and reproducibility before declaring a "
    "security issue. Correlate with other telemetry where possible."
)

STATIC_NEXT_STEP = (
    "Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where "
    "applicable, remediate, and verify."
)

STATIC_COMMON_MISTAKES = [
    "Using an asset outside the approved scope",
    "Treating tool output as proof without validation",
    "Ignoring evidence provenance or timestamps",
]

STATIC_DEFAULT_EVIDENCE = ["tool output",
                           "target/scope", "timestamp", "provenance"]

STATIC_BOUNDARY = (
    "Governed security operations. VEYRA enables authorized security testing, "
    "red-team, blue-team, and defensive work on owned or explicitly permitted "
    "targets. Tools are tiered by risk: Standard (discovery, analysis, "
    "defensive verification), Privileged (high-impact testing requires "
    "privileged_admin and an approved engagement), and Isolated Lab Only "
    "(attack-capable tools may only run against lab/sandbox targets). All "
    "executions are scope-bound, evidence-captured, and audited. Out-of-scope "
    "activity, unowned targets, and unauthorized use are prohibited."
)

STATIC_DEFAULT_SAFE_WORKFLOW = (
    "Use the tool for its documented supporting security task inside an "
    "approved worker, inspect output, and preserve relevant evidence."
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def load_tools() -> dict[str, dict]:
    """Merge all three registries, keyed by tool id."""
    tools: dict[str, dict] = {}
    for t in extended_registry() + ai_cut() + ai_ecosys():
        tid = t.get("id") or t.get("tool_id") or t.get("name", "")
        if not tid:
            continue
        tools.setdefault(tid, t)
    return tools


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

def render_doc(tool: dict) -> str:
    name = tool["name"]
    category = tool["category"]
    purpose = tool["purpose"]
    access = tool.get("access_tier", "admin")
    boundary = tool.get("execution_profile", "approved_worker")
    h = tool.get("help", {}) or {}

    evidence = h.get("expected_evidence", STATIC_DEFAULT_EVIDENCE)
    mistakes = h.get("common_mistakes", STATIC_COMMON_MISTAKES)

    lines: list[str] = [
        f"# {name}",
        "",
        f"**Category:** {category}  ",
        f"**Purpose:** {purpose}  ",
        f"**VEYRA access:** {access}  ",
        f"**Execution boundary:** {boundary}",
        "",
        "## What is it?",
        h.get("summary", purpose),
        "",
        "## Why VEYRA includes it",
        h.get("why_veyra", STATIC_WHY_VEYRA),
        "",
        "## When should the team use it?",
        f"Use it when the security objective matches **{purpose}** and the "
        f"target is owned, explicitly authorized, and inside the recorded scope.",
        "",
        "## VEYRA UI workflow",
        *[line.format(name=name) for line in STATIC_UI_WORKFLOW],
        "",
        "## Terminal starting point",
        STATIC_TERMINAL_INTRO,
        "",
        "```bash",
        f"{name} --help",
        f"{name} --version",
        "```",
        "",
        STATIC_TERMINAL_NOTES_1,
        "",
        STATIC_TERMINAL_NOTES_2,
        "",
        "## Safe workflow",
        h.get("safe_workflow", STATIC_DEFAULT_SAFE_WORKFLOW),
        "",
        "## Evidence to collect",
        *[f"- {item}" for item in evidence],
        "",
        "## How to interpret results",
        STATIC_INTERPRET,
        "",
        "## Remediation and verification",
        h.get("next_step", STATIC_NEXT_STEP),
        "",
        "## Common mistakes",
        *[f"- {item}" for item in mistakes],
        "",
        "## Team teaching summary",
        f"**One sentence:** {name} is used to help the team achieve "
        f"**{purpose}** under an approved and auditable VEYRA workflow.",
        "",
        "## Security boundary",
        h.get("help_boundary", STATIC_BOUNDARY),
    ]

    # File ends with a single trailing newline
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="Do not write; exit 1 if any doc would change")
    ap.add_argument("--verbose", action="store_true",
                    help="Print every file written/changed")
    args = ap.parse_args()

    tools = load_tools()
    DOCS.mkdir(parents=True, exist_ok=True)

    total = 0
    changed = 0
    missing = 0

    for tid, tool in sorted(tools.items()):
        total += 1
        target = DOCS / f"{tid}.md"
        rendered = render_doc(tool)

        if target.exists():
            current = target.read_text(encoding="utf-8")
            if current == rendered:
                continue
            changed += 1
            if args.verbose:
                print(f"  CHANGED  {target.relative_to(REPO)}")
        else:
            missing += 1
            if args.verbose:
                print(f"  MISSING  {target.relative_to(REPO)}")

        if not args.check:
            target.write_text(rendered, encoding="utf-8")

    mode = "CHECK" if args.check else "WRITE"
    print(f"Mode:            {mode}")
    print(f"Registered:      {total}")
    print(f"Missing:         {missing}")
    print(f"Changed:         {changed}")

    if args.check and (missing or changed):
        print()
        print("Run `python scripts/generate_tool_docs.py` to write changes.")
        return 1
    if not args.check:
        print()
        print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
