# VEYRA v3.7 — Security Graph Intelligence

## Purpose

VEYRA v3.7 turns the existing Security Graph into a read-only intelligence layer that correlates assets, identities, cloud resources, AI assets, findings, incidents, governed jobs and evidence receipts.

The product lifecycle remains:

**Discover → Understand → Validate → Investigate → Correlate → Contain → Recover → Prove → Learn → Continuously revalidate.**

## Why this matters

The graph is the place where point findings become explainable security relationships. VEYRA should be able to show not only that a finding exists, but what it is connected to, which controls it affects, what evidence supports the relationship, and whether the relationship creates an attack-path or remediation hotspot.

## UI workflow

1. Open **Graph Intelligence**.
2. Review graph node/relationship counts.
3. Inspect graph hotspots and chokepoints.
4. Review correlated attack paths.
5. Switch to **Controls & evidence**.
6. Review control coverage and evidence receipts.
7. Investigate the underlying asset, finding, incident or evidence record before requesting any response action.

## API

- `GET /api/v37/security-graph/intelligence`
- `GET /api/v37/security-graph/control-evidence`

Both endpoints are admin-gated and read-only.

## Control mappings

The v3.7 read model currently correlates to NIST CSF 2.0, OWASP Agentic Applications 2026, OWASP Agent Control Standard, MITRE ATT&CK and supply-chain trust concepts such as SLSA, Sigstore and TUF.

NIST CSF 2.0 defines six concurrent Functions: Govern, Identify, Protect, Detect, Respond and Recover. VEYRA's lifecycle is intentionally operational rather than a replacement for the framework. citeturn0search14turn0search2

OWASP's 2026 Agent Control Standard emphasizes that agents should be inspectable, traceable and instrumentable and that runtime controls should be enforceable through standardized hooks. This is directly relevant to VEYRA's agent/tool relationship graph. citeturn0search12

MITRE ATLAS remains a living AI-threat knowledge base covering predictive, generative and agentic AI systems. citeturn0search18

## Evidence expectations

A graph relationship should be treated as stronger when it has provenance such as:

- collector/source
- timestamp
- governed job ID
- artifact ID
- SHA-256
- worker provenance
- control mapping
- supporting finding/incident

AI-generated explanations must cite these underlying records. The model is not the source of truth.

## Remediation workflow

For a high-risk hotspot:

1. Identify the underlying asset/identity/cloud/AI record.
2. Verify the relationship with available evidence.
3. Confirm written scope and authorization.
4. Determine whether the problem is exposure, identity, configuration, detection, supply chain or runtime control.
5. Stage a bounded remediation/containment plan through the existing approval path.
6. Capture the action receipt.
7. Revalidate the original relationship and control.
8. Preserve evidence and record the learning.

## Security boundary

This service does **not** execute commands, perform hack-back, disable controls, expose an unrestricted browser shell or autonomously contain systems. It is a correlation and evidence layer over the existing governed architecture.

## Team training summary

Think of the graph as the security team's shared map:

**What is connected? Why is it connected? What proves it? What control does it affect? What changed? What should we verify next?**
