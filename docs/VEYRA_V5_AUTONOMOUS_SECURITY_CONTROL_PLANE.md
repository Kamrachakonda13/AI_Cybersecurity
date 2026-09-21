# VEYRA v5.0 — Autonomous Security Control Plane

## Purpose

VEYRA v5.0 unifies the v4.0 Tool Supply Chain, v4.1 Verified Worker Runtime, v4.2 Trusted Supply Chain Fabric, v4.3 AI/Agent Supply Chain and v4.4 Continuous Trust Graph into one governed control plane.

> **No tool, model, agent, MCP server, artifact or update becomes trusted merely because it exists. It must establish identity, provenance, integrity, policy compliance, validation, controlled deployment and observable runtime behavior.**

## Trust domains

- traditional security tools and managed workers
- models and model adapters
- agents and agent cards
- MCP servers and tools
- A2A endpoints and delegation chains
- prompts, skills and deployment wrappers
- datasets, RAG corpora, embeddings and vector indexes
- identities, endpoints, cloud resources and network destinations
- evidence, attestations and security decisions

## 11 mandatory gates

1. Identity
2. Provenance
3. Integrity
4. Policy compliance
5. Validation
6. Deployment control
7. Runtime attestation
8. Behavioral baseline
9. Trajectory assurance
10. Evidence integrity
11. Circuit-breaker readiness

Registration is inventory only. A registered asset remains untrusted until the gates are satisfied.

## v5.0 APIs

- `GET /api/v50/overview`
- `GET /api/v50/gates`
- `POST /api/v50/ai-assets/register`
- `GET /api/v50/ai-assets`
- `POST /api/v50/aibom/generate`
- `POST /api/v50/trajectory/evaluate`
- `POST /api/v50/trust/decide`
- `POST /api/v50/trust-graph/rebuild`
- `GET /api/v50/trust-graph`
- `POST /api/v50/runtime-attestation`
- `POST /api/v50/mandates`
- `GET /api/v50/decisions`

## Runtime contract

The control plane creates decisions and signed/observable contracts. Actual enforcement belongs to authorized managed workers, workload identity, MCP/A2A gateways, network policy and other external policy points.

VEYRA does not expose arbitrary shell execution or unrestricted offensive automation through these APIs.

## Research-aligned design

Current 2026 security guidance increasingly treats MCP servers as supply-chain dependencies and recommends approved publishers, tool metadata inspection, least privilege, human approval for high-impact actions and correlation of agent/tool telemetry. NSA has published dedicated MCP security design considerations, while Microsoft describes tool-poisoning risks and recommends allowlisting and runtime correlation. These principles are incorporated here as control-plane requirements rather than trusted-by-default integrations.

Sigstore/SLSA-style build provenance and runtime workload identity are complementary: build-time evidence establishes how an agent artifact was produced; runtime attestation establishes which workload is actually serving it.

## Safety boundary

No hack-back, persistence, C2, destructive action, unrestricted credential attack or arbitrary command execution is exposed by the v5.0 control plane. High-impact actions remain approval-gated and evidence-backed.
