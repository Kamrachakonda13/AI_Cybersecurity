# VEYRA v3.2 — Team Security Academy & Documentation Fabric

## Purpose

v3.2 turns the VEYRA security-tool catalog into a team-operational learning system. The product now treats documentation as a release artifact: every registered tool must have a consistent explanation of purpose, when to use it, UI workflow, terminal starting point, permissions, scope, evidence, interpretation, remediation, verification and common mistakes.

## New capabilities

- Team Security Academy UI.
- Role-based learning tracks: SOC/Blue Team, Red/Purple Team, AI Security, Cloud/Kubernetes, DFIR/Malware and Security Engineering.
- Four learning levels: Beginner, Intermediate, Advanced, Expert.
- API curriculum endpoints under `/api/v32/academy/*`.
- Individual Markdown help page for every registered tool under `docs/tools/`.
- AI security reference updated against current OWASP 2026 material, NIST AI RMF resources and Google SAIF.
- Documentation index linking the complete tool catalog to the team learning model.

## Safety and execution model

Documentation is educational and operational guidance. It does not grant execution rights. Security tooling remains governed by identity, role, scope, approval, managed worker, evidence and audit controls. VEYRA does not expose an unrestricted browser shell and does not support hack-back or counter-intrusion.

## AI-security baseline

The v3.2 AI curriculum explicitly covers LLM security, agent security, MCP, A2A, prompt/context security, memory, RAG, vector stores, model artifacts, adversarial ML, AI supply chain, AI observability, AI governance, threat intelligence and incident response.
