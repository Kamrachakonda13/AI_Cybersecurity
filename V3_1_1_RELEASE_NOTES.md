# VEYRA v3.1.1 — Complete Tool Help & Cutting-Edge AI Security Baseline

## What changed

- Expanded the VEYRA tool operating manual from a compact index to a **tool-by-tool team training reference**.
- Every catalog entry now has an explanation, UI workflow, terminal starting point, expected evidence, common mistakes and next-step guidance.
- Expanded the AI security ecosystem with the current 2026 baseline for LLM red teaming, agent evaluation, MCP, A2A, guardrails, observability, RAG, model security, adversarial ML and AI supply chain.
- Added `AI_CUTTING_EDGE_2026_TEAM_GUIDE.md`.
- Updated `AI_LATEST_2026.md`.
- Preserved Sudo, approval, worker isolation, evidence and anti-hack-back boundaries.

## Catalog size

**577 tools/integrations** after de-duplication across the core Kali-derived catalog, VEYRA security extensions and 2026 AI security additions.

## Documentation contract

Any future tool addition or meaningful behavior change must update:

1. tool registry metadata;
2. `docs/TOOL_USAGE_CATALOG_V31.md`;
3. relevant domain guide;
4. `README.md` / runbook when user-visible behavior changes;
5. tests for registry/API behavior.
