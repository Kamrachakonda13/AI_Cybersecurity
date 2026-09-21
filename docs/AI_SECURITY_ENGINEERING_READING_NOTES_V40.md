# AI Security Engineering — VEYRA v4.0 design notes

Ashish Rajan's 2026 Wiley book positions AI security as an engineering discipline for dependable AI in production, emphasizing threat models, secure pipelines, runtime detection/response, governance and agentic/multi-model systems.

VEYRA v4.0 maps those ideas into product controls:

| AI security engineering idea | VEYRA implementation |
|---|---|
| Threat modeling | Security Graph, attack paths, AI Research Lab, agent containment |
| Secure pipelines | Tool Supply Chain, artifact verification, provenance, SBOM |
| Runtime detection | Agent runtime telemetry, rogue-agent detection, swarm-risk simulation |
| Runtime response | Approval-gated SOAR + containment policy + emergency stop state |
| Governance | RBAC, Sudo, approvals, scope, audit, update policies |
| Agentic systems | Agent identity/policy, tool allowlists, evidence-backed investigations |
| Continuous assurance | health checks, canary channels, posture snapshots, rollback |

The book should be treated as a conceptual reference, not copied into the product. VEYRA's implementation remains original and focuses on an operational control plane.
