# VEYRA v4.2 — Trusted Supply Chain Fabric

## Ultimate invariant

> No tool, model, agent, MCP server, artifact or update becomes trusted merely because it exists. It must establish identity, provenance, integrity, policy compliance, validation, controlled deployment and observable runtime behavior.

## Trust lifecycle

```text
Discovery → Identity → Provenance → Integrity → Policy → Validation → Canary → Stable → Runtime Observation
                                           │                                      │
                                           └──────────── failure ────────────────┘
                                                          ↓
                                                     Rollback
```

## Verification gates

1. identity
2. artifact digest
3. signature
4. provenance
5. SBOM
6. vulnerability scan
7. smoke test
8. parser regression
9. security regression
10. policy compliance
11. runtime observability

## Supply-chain integrations

- TUF — update metadata, freshness and rollback/freeze protection.
- Cosign/Sigstore — artifact signatures and attestations.
- Syft — SBOM generation.
- Grype — vulnerability scanning.
- SLSA v1.2 / in-toto — provenance and attestations.

SLSA v1.2 is the current approved specification and defines provenance as verifiable information about where, when and how an artifact was produced. See the official specification: https://slsa.dev/spec/v1.2/.

## AI supply chain

The same trust lifecycle applies to:

- models
- model adapters
- datasets
- agent packages
- MCP servers
- A2A services
- prompt packages
- vector indexes
- evaluation assets

Each asset should eventually have an AIBOM/AI supply-chain identity, immutable digest, provenance, policy status and runtime telemetry.

## Circuit breaker

AI agents receive an external control path. A circuit breaker is an auditable control-plane decision; enforcement remains in the managed identity/network/worker plane.

## Security boundary

The SaaS control plane never accepts arbitrary shell commands. Worker verification uses a fixed allowlist of verification binaries and returns structured receipts rather than unbounded command output.
