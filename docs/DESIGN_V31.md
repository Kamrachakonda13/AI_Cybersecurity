# VEYRA v3.1 — Design Specification

## Release
**3.1.0 — Sudo Security Arsenal & Adversary Trace Fabric**

## Goals
1. Give Sudo users a comprehensive governed security-tool catalog.
2. Make UI and terminal usage consistent and documented.
3. Add a defensive adversary-trace workflow for active incidents.
4. Keep all third-party execution on authenticated managed workers.
5. Make evidence, provenance, SBOM and audit first-class outputs.

## New API
- `GET /api/v31/arsenal/overview`
- `GET /api/v31/arsenal/tools`
- `GET /api/v31/arsenal/tools/{tool_id}`
- `POST /api/v31/trace/plan`

## New documentation
- `docs/SUDO_SECURITY_ARSENAL_V31.md`
- `docs/ADVERSARY_TRACE_V31.md`
- `docs/TOOL_USAGE_CATALOG_V31.md`
- `docs/TERMINAL_RUNBOOK_V31.md`
- this design document

## Operational principle
VEYRA is a control plane. It does not become a generalized remote shell merely because a user has Sudo. The privileged role controls capability; the worker controls execution; the evidence layer controls accountability.
