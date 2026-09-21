# VEYRA Production Hardening Checklist v3.4

- Enforce SSO/OIDC + MFA for production administrators.
- Keep Sudo grants time-limited and scope-bound.
- Isolate workers from the SaaS control plane and restrict egress.
- Pin tool versions and verify signatures/hashes where available.
- Maintain SBOM/AIBOM and dependency/model provenance.
- Encrypt evidence at rest and in transit; apply retention and legal-hold policy.
- Keep tenant data isolated at the database, object-storage and worker layers.
- Use short-lived workload identity for workers and connectors.
- Log policy decisions, approvals, tool requests, execution receipts and evidence hashes.
- Protect AI agents with deterministic runtime policy outside the model.
- Monitor MCP/A2A/tool calls and high-impact actions.
- Exercise containment and recovery regularly.
- Run documentation validation in CI before release.
- Back up databases, configuration, policy and evidence indexes; test restoration.
- Treat attribution as a hypothesis supported by evidence, not as an automatic fact.
