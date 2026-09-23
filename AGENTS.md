# AGENTS.md

## Purpose

This repository is the VEYRA v5 autonomous security control plane: a governed security operations platform with a Python backend, React frontend, managed workers, and a large docs/tool catalog. AI coding agents should optimize for safety, traceability, and evidence-first changes.

## Where to start

- Project overview and quick start: [README.md](README.md)
- CI and validation gates: [.github/workflows/ci.yml](.github/workflows/ci.yml)
- Platform architecture and SaaS plan: [SaaS_Platform_Ready_Plan.md](SaaS_Platform_Ready_Plan.md)
- Core application code: [backend/app](backend/app)
- Frontend app: [frontend/src](frontend/src)
- Worker runtime: [worker](worker)
- Documentation and tool catalog: [docs](docs)

## Operating conventions

- Prefer minimal, surgical changes that align with existing patterns.
- Keep security boundaries in mind: do not introduce arbitrary execution, unsafe network behavior, or unapproved privileged actions.
- Preserve evidence provenance, auditability, and approval-gated flows when touching defense/security logic.
- If you change runtime behavior, add or update the most relevant tests in the nearest existing suite.
- Favor explicit validation over broad assumptions; run the smallest relevant check for the changed layer.

## Validation commands

### Backend

```bash
cd backend
PYTHONPATH=. pytest -q
```

For coverage-oriented validation:

```bash
cd backend
PYTHONPATH=. pytest -q --cov=app --cov-report=term-missing
```

### Frontend

```bash
dcd frontend
npm ci
npm run test
```

For build verification:

```bash
cd frontend
npm ci
npm run build
```

### Docs / generated metadata

```bash
cd backend
PYTHONPATH=backend python scripts/validate_tool_documentation.py
PYTHONPATH=backend python scripts/generate_tool_docs.py --check
PYTHONPATH=backend python scripts/validate_checklists.py
```

## Repository shape

- `backend/` contains the API, services, models, and tests.
- `frontend/` contains the React app and frontend tests.
- `worker/` contains the managed worker runtime, Docker assets, and operational logic.
- `docs/` contains architecture, runbooks, and product documentation.
- `tests/` and `backend/tests/` hold higher-level regression tests.
- `scripts/` contains validation and document-generation utilities.

## Safety and implementation guidance

- Do not weaken approval gates, validation checks, or tenant/resource isolation patterns.
- Do not hardcode secrets or sensitive config in code or docs.
- Keep generated docs and source-of-truth catalogs in sync when changing tool metadata or docs.
- For API and service changes, prefer the existing model/service routing patterns used by the repo.
- For frontend work, keep tests aligned with the current Vitest + Testing Library setup.

## Helpful references

- [README.md](README.md)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [SaaS_Platform_Ready_Plan.md](SaaS_Platform_Ready_Plan.md)
- [backend/requirements.txt](backend/requirements.txt)
- [frontend/package.json](frontend/package.json)

This file is intentionally brief; use the linked docs above for deeper architecture, security model, and operating details.
