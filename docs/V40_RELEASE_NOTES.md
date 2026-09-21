# VEYRA v4.0 Release Notes

## Tool Supply Chain & Autonomous Update Fabric

### Added

- ToolDefinition / ToolRelease / ToolArtifact / ToolUpdatePolicy / ToolDeployment / ToolHealthCheck models.
- Update Scout and upstream source registry.
- Candidate → Canary → Stable → Extended Stable channels.
- Floating / pinned / immutable version policy.
- Force-update and first-class rollback planning.
- Freeze and quarantine controls.
- Signed worker manifest generation with optional Ed25519 signing key.
- Immutable artifact metadata and SHA-256 identity.
- Health/regression evidence gate.
- Worker receipt acknowledgement endpoint.
- Alembic migration structure.
- TUF / Cosign / Syft / Grype verification adapter inventory.
- AI Swarm Containment policy and simulator.
- Hydejack-inspired Documentation Hub.

### Important production requirements

1. Configure `VEYRA_UPDATE_SIGNING_PRIVATE_KEY` through a real secret manager; never commit it.
2. Put artifact bytes in immutable object storage with retention/locking.
3. Run TUF/Cosign/Syft/Grype/SLSA verification inside isolated workers.
4. Use workload identity and signed worker requests before production rollout.
5. Make Alembic migrations the production schema authority.
6. Keep automatic production updates disabled until tenant-specific canary/rollback SLOs are proven.
