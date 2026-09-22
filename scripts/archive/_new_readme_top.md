# VEYRA v5.0 — Autonomous Security Control Plane

**SEE • REASON • VALIDATE • DEFEND**

[![VEYRA CI](https://github.com/Kamrachakonda13/veyra/actions/workflows/ci.yml/badge.svg)](https://github.com/Kamrachakonda13/veyra/actions/workflows/ci.yml)
[![Secret scan](https://github.com/Kamrachakonda13/veyra/actions/workflows/secret-scan.yml/badge.svg)](https://github.com/Kamrachakonda13/veyra/actions/workflows/secret-scan.yml)
[![Tests](https://img.shields.io/badge/tests-382%20passing-brightgreen)](#testing)
[![Backend coverage](https://img.shields.io/badge/backend%20coverage-75%25-brightgreen)](#testing)
[![Frontend coverage](https://img.shields.io/badge/frontend%20coverage-setup%20only-yellow)](#testing)
[![Branding](https://img.shields.io/badge/branding-VEYRA-blue)](#)

VEYRA is a security control plane that correlates network, endpoint, identity,
cloud, data and AI-security signals into one operational model with an
explainable risk engine, a Security Graph with attack-path analysis, governed
assessment jobs, static forensics, and separate Red/Blue team workflows.

**v5.0** consolidates the security operations, continuous validation, security
graph, tool supply-chain, verified worker runtime, trusted supply-chain,
AI/agent supply-chain and continuous trust capabilities into a single governed
control plane. It includes six portfolio-grade AI applications and full-stack
test coverage enforced in CI.

## Quick start

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export CORS_ORIGINS=http://localhost:3000
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

### Docker Compose

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Frontend: http://localhost:3000
API docs: http://localhost:8000/docs
Health: http://localhost:8000/health

## v5 control plane

Open **VEYRA v5 Control Plane** in the console. It provides:

- 11 trust gates
- AI/agent supply-chain inventory
- AIBOM generation API
- trajectory-level assurance
- unified trust graph
- runtime attestation
- signed mandate records
- evidence-backed trust decisions
- circuit-breaker readiness

See [`docs/VEYRA_V5_AUTONOMOUS_SECURITY_CONTROL_PLANE.md`](docs/VEYRA_V5_AUTONOMOUS_SECURITY_CONTROL_PLANE.md)
and [`docs/VEYRA_V5_PRODUCTION_RUNBOOK.md`](docs/VEYRA_V5_PRODUCTION_RUNBOOK.md).

## Testing

VEYRA has full-stack test coverage enforced in CI.

### Backend

```bash
cd backend
PYTHONPATH=. pytest -q                                       # 365 tests
PYTHONPATH=. pytest -q --cov --cov-report=term-missing       # with coverage
```

- **365 tests** across all services and API routes
- **75% line coverage** (via `pytest-cov`)
- **100% service coverage** — every module in `backend/app/services/` has direct tests

### Frontend

```bash
cd frontend
npm ci
npm test                # 17 tests
npm run test:coverage   # with coverage
```

- **17 tests** covering structural invariants (storage keys, auth headers, branding)
- Test infrastructure: **vitest** + **@testing-library/react** + **jsdom**

### CI

All checks run on every push (see [`.github/workflows/ci.yml`](.github/workflows/ci.yml)):

- `backend` — pytest + coverage + compileall
- `docs` — tool documentation validator (587 tools, full content check)
- `docs-drift` — generator `--check` (zero drift)
- `frontend` — npm build + npm test with coverage
- `security supply-chain gates` — pytest on supply-chain modules + compileall
- `Secret scan` — gitleaks

## Security boundary

The SaaS/API control plane does not provide arbitrary shell execution, hack-back,
persistence, C2, destructive actions or unrestricted credential attacks.
High-impact actions remain governed by authorization, approval, managed-worker
contracts and evidence.

## Production status

This is a final integrated engineering release, but production trust still
depends on deploying real infrastructure for TUF, Sigstore, SLSA/in-toto, SBOM
scanning, workload identity, immutable artifact storage, managed workers,
network/identity enforcement and tenant isolation.

## Final AI Applications Layer

VEYRA v5.0 includes six portfolio-grade applications:

- **CyberSOC RAG** — AI security analyst with hybrid evidence retrieval
- **Vulnerability Intelligence RAG** — risk-aware CVE/asset/KEV prioritization
- **Autonomous Research Agent** — planner → search → retrieval → fact-check workflow
- **Agentic Incident Response** — evidence-driven investigation with MITRE mapping
- **Enterprise AI Knowledge & Decision Platform** — governed router pattern
- **LLM Evaluation & AI Reliability** — RAG/agent/model evaluation with release gates

See [`docs/AI_APPLICATIONS_POC_FINAL_V50.md`](docs/AI_APPLICATIONS_POC_FINAL_V50.md).

---

## 📚 Full platform reference

The sections below document the complete VEYRA platform: architecture, tool
ecosystem, safety model, codebase guide and historical release notes.