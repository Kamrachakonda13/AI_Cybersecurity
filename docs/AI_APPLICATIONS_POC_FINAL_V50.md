# VEYRA v5.0 — AI Applications POC Final Layer

## Purpose

This final layer turns the six portfolio POCs into first-class applications on one governed VEYRA AI platform. The implementations use deterministic demo fixtures and explicit connector seams so a production deployment can replace fixtures with approved data, model, search, SQL, web-research and telemetry providers without changing the trust boundary.

## Six applications

1. **CyberSOC RAG — AI Security Analyst** — hybrid retrieval, evidence, citations, MITRE/security correlation, grounded investigation.
2. **Vulnerability Intelligence RAG** — CVE + asset + KEV + exposure + criticality prioritization and remediation reasoning.
3. **Autonomous Research Agent** — planner, search, retrieval, analyst, fact-checker, critic and report-generation stages.
4. **Agentic Cybersecurity Incident Response** — timeline, investigation evidence, MITRE mapping, risk and approval-gated containment recommendation.
5. **Enterprise AI Knowledge & Decision Platform** — governed router pattern for RAG plus structured-data/API/SQL/graph connector seams.
6. **LLM Evaluation & AI Reliability Platform** — RAG/agent/model metrics and release gates for quality, grounding, tool use, cost and latency.

## Shared platform

All six applications share VEYRA identity, policy, evidence, trust graph, AI supply-chain, agent gateway, runtime assurance and audit controls. No application exposes arbitrary shell, unrestricted offensive automation, credential attacks, persistence, C2 or destructive actions.

## Production connector seams

- Search: BM25/OpenSearch/Elasticsearch
- Vector: Qdrant/Pinecone/Weaviate/pgvector
- Reranking: approved reranker service
- LLM: provider-neutral adapter
- Agents: LangGraph-compatible orchestration seam
- Knowledge graph: Neo4j-compatible graph seam
- Evaluation: RAGAS/DeepEval/custom benchmark seam
- Observability: OpenTelemetry/LangSmith/Langfuse-compatible seam
- Security data: SIEM, NVD/CVE, CISA KEV, MITRE ATT&CK, SBOM and asset inventory adapters

## Evidence contract

Every run has an application ID, run ID, request/result record and SHA-256 evidence identity. Production deployments should additionally bind model/provider metadata, dataset snapshot, prompt package, retrieval corpus/index version, policy hash, workload identity and runtime attestation.
