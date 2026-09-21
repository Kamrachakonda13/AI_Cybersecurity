# VEYRA v3.0 — Full Security Operations Fabric

## Added

- Unified Full Security Operations Fabric dashboard.
- Unified Security Graph read model spanning assets, identities, AI assets, cloud resources, services and network flows.
- AI Attack Reconstruction timeline across findings, sessions, high-risk network flows and audit events.
- AI SOC Investigator signal prioritization and reasoning contract.
- Governed Response & Recovery console with approval-required containment plans.
- Recovery verification checks for open high-risk findings, unexpected services and high-risk flows.
- v3.0 API under `/api/v3/fabric/*`.
- v3.0 documentation and tests.

## Safety model

The API remains non-destructive. Response actions are plans only; actual containment requires policy approval and a managed worker. Attribution remains hypothesis-only.

## Validation

- Python compilation: passed.
- New v3 service tests: included.
- Full inherited suite: run from `backend` with `PYTHONPATH=.`; legacy/shared-database failures may remain in the inherited test set.
- Frontend dependency installation/build was not claimed unless successfully executed in the target environment.


## v3.1 follow-on
See `docs/DESIGN_V31.md`, `docs/SUDO_SECURITY_ARSENAL_V31.md`, `docs/ADVERSARY_TRACE_V31.md`, `docs/TOOL_USAGE_CATALOG_V31.md`, and `docs/TERMINAL_RUNBOOK_V31.md`.
