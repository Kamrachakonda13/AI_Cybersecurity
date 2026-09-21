# VEYRA v3.6 Production Audit

## Scope

Reviewed the v3.5 project tree, backend service/catalog structure, 588-tool registry, 589 Markdown files under `docs/tools`, lifecycle APIs, frontend routing, tests, release metadata and current 2026 ecosystem recommendations.

## Findings fixed in v3.6

- Added 11 current ecosystem integrations/candidates.
- Added a Security Radar separating recommended and experimental projects.
- Added OWASP Agent Control Standard and GenAI framework crosswalk as explicit control references.
- Added per-tool documentation for every newly cataloged integration.
- Added tool-promotion governance criteria.
- Pinned frontend dependency versions instead of using `latest`, improving reproducibility.
- Added a v3.6 release manifest with hashes for key release artifacts.

## Validation

- Python compilation: PASS.
- Documentation gate: **588 registered / 588 complete / 0 missing / 0 incomplete**.
- Targeted v3.2/v3.4/v3.5 tests: **6 passed**.
- Full historical suite: **66 passed / 7 failed**. The seven failures are legacy/shared-state or test-order-sensitive failures, including duplicate fixture IDs and route tests that inherit a mutated global SQLAlchemy `SessionLocal`. They are retained as a release hardening backlog rather than being hidden.
- Frontend production build: not completed in the sandbox because npm package installation timed out and the environment lacks the resolved Vite binary. The package manifest is now pinned to the versions represented in the lockfile.

## Release hygiene

The source workspace contains generated Python caches and local SQLite state from development. The distributable v3.6 ZIP excludes `__pycache__`, `.pytest_cache`, local SQLite databases and `node_modules`; runtime state should be created by deployment rather than shipped as source.

## Security boundary

No new capability grants arbitrary browser shell access or hack-back. Experimental agent/MCP tools remain isolated and require authorization, scope, approval and evidence controls before execution.
