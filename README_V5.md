# VEYRA v5.0 — Autonomous Security Control Plane

**SEE • REASON • VALIDATE • DEFEND**

This final release consolidates the VEYRA security operations, continuous validation, security graph, tool supply-chain, verified worker runtime, trusted supply-chain, AI/agent supply-chain and continuous trust capabilities into a single governed control plane.

## Start

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

See `docs/VEYRA_V5_AUTONOMOUS_SECURITY_CONTROL_PLANE.md` and `docs/VEYRA_V5_PRODUCTION_RUNBOOK.md`.

## Security boundary

The SaaS/API control plane does not provide arbitrary shell execution, hack-back, persistence, C2, destructive actions or unrestricted credential attacks. High-impact actions remain governed by authorization, approval, managed-worker contracts and evidence.

## Production status

This is a final integrated engineering release, but production trust still depends on deploying real infrastructure for TUF, Sigstore, SLSA/in-toto, SBOM scanning, workload identity, immutable artifact storage, managed workers, network/identity enforcement and tenant isolation.


## Final AI Applications Layer

VEYRA v5.0 includes six portfolio-grade applications: CyberSOC RAG, Vulnerability Intelligence RAG, Autonomous Research Agent, Agentic Incident Response, Enterprise AI Knowledge & Decision Platform, and LLM Evaluation & AI Reliability. See `docs/AI_APPLICATIONS_POC_FINAL_V50.md`.
