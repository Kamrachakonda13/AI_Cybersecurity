# VEYRA v5.0 Production Runbook

## 1. Before deployment

- PostgreSQL production database
- HTTPS and secure CORS
- SSO/OIDC + MFA for administrators
- short-lived workload identities
- isolated managed workers
- immutable artifact storage/WORM controls
- real TUF root metadata and freshness policy
- Sigstore/Cosign verification policy
- SLSA/in-toto provenance acceptance
- Syft SBOM generation and Grype policy
- tenant/workspace-specific update policies
- signed worker pull queue
- external network/identity circuit-breaker integration

## 2. Trust onboarding

1. Register the asset.
2. Record immutable digest.
3. establish publisher/workload identity.
4. attach provenance and SBOM/AIBOM.
5. validate security and behavioral baseline.
6. create controlled deployment contract.
7. collect runtime attestation.
8. evaluate trajectory policy.
9. record evidence hash.
10. promote only when every required gate passes.

## 3. Incident mode

If trust drops below policy:

1. preserve evidence;
2. deny new high-impact actions;
3. activate the external circuit breaker where authorized;
4. revoke/quarantine the affected identity or integration;
5. preserve model/tool/MCP/A2A versions and hashes;
6. investigate dependency and delegation graph;
7. remediate and revalidate;
8. only then restore trust.

## 4. Release verification

Run the managed-worker verifier only with a structured allowlisted verifier name and immutable SHA-256 subject. Never pass arbitrary shell text through the SaaS API.
