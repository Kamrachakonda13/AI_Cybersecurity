# VEYRA POC Roadmap

## v1 completed
- Security console shell
- Asset inventory
- Port/service/process/user attribution model
- Findings and incidents
- Explainable risk engine
- AI advisory investigation endpoint
- Assessment scope/approval boundary
- PostgreSQL persistence
- Docker Compose

## v1.1 completed in this increment
- Identity and privileged-account inventory
- Session telemetry model
- Network flow telemetry model
- Threat-intelligence records with CISA KEV / MITRE-style correlation hooks
- Cloud resource posture model
- AI asset inventory including agents and vector databases
- Expanded overview KPIs
- AI investigation evidence bundle includes known-exploited intelligence

## v1.5 production build (this increment — all 13 slices closed)
- Live CISA KEV + NVD ingestion (`services/threatintel.py`, `CveRecord`, refresh endpoint, 24h scheduler)
- MITRE ATT&CK knowledge + finding coverage (`services/mitre.py`, 16 techniques incl. 2 ATLAS concepts)
- Attack-path hardening: per-path risk + choke-point ranking (`services/graph.py`)
- Endpoint agent (`collectors/endpoint-agent.py`: heartbeat, ports, USB, DLP-lite) + token-gated ingest
- Cloud adapters: Prowler-JSON import + live read-only AWS scan (`services/cloud_adapters.py`)
- AI red evaluation battery + vector-DB tenant enforcement + retrieval audit (`services/ai_red.py`, `services/vectordb.py`)
- USB/DlpEvent models + auto-findings + Endpoint panels
- SOAR engine: 4 playbooks, approval-gated runs, DB-safe execution (`services/soar.py`, Governance panel)
- Production guide (tokens, schedules, backups) + compose env passthrough

## Next implementation slices (operations, not features)
1. Real authorized endpoint collector (Linux/macOS lab)
2. Network flow + DNS ingestion pipeline
3. NVD/CISA KEV live ingestion with normalized CVE model
4. MITRE ATT&CK knowledge service + grounded RAG with citations
5. Cloud posture adapters for AWS/Azure/GCP
6. AI security controls: prompt injection, tool permissions, agent action audit
7. Vector DB security: tenant boundaries, metadata classification, retrieval audit
8. USB/device telemetry + DLP correlation
9. Attack-path/security graph service
10. SOAR playbooks with approval + verification
11. OpenTelemetry, Prometheus and Grafana
12. OIDC/RBAC/ABAC and multi-tenant isolation
13. Kubernetes/Terraform production deployment

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
