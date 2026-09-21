# VEYRA v3.0 — Full Security Operations Fabric

## Purpose

v3.0 unifies the existing VEYRA telemetry, Security Graph, wireless defense, endpoint attribution, cloud posture, AI security, threat intelligence, DFIR and managed-worker architecture into one operational control plane.

## Operational lifecycle

`Detect → Preserve → Investigate → Correlate → Reconstruct → Enrich → Attribute → Contain → Recover → Verify → Learn`

The v3 API currently exposes read models and governed response planning:

- `GET /api/v3/fabric/overview`
- `GET /api/v3/fabric/graph`
- `GET /api/v3/fabric/reconstruction`
- `GET /api/v3/fabric/ai-investigation`
- `POST /api/v3/fabric/response-plan`
- `GET /api/v3/fabric/recovery`

## Architecture

```text
Collectors / Cloud / AI / Network / Wireless / Identity
                    |
                    v
             VEYRA Telemetry
                    |
                    v
          Deterministic Correlation
                    |
          +---------+---------+
          |                   |
          v                   v
    Security Graph       AI Investigator
          |                   |
          +---------+---------+
                    v
             Attack Reconstruction
                    |
                    v
          Threat Intelligence Fusion
                    |
                    v
          Attribution Hypotheses
                    |
                    v
          Human Verification Gate
                    |
                    v
       Governed Response / SOAR Plan
                    |
                    v
              Managed Worker
                    |
                    v
        Verification + Evidence
```

## Defensive control boundary

VEYRA does not provide hack-back, destructive retaliation, credential theft, persistence, deauthentication, or an unrestricted browser shell. High-impact response is staged for approval and execution through the managed worker boundary.

## AI investigation contract

The AI investigator should treat deterministic telemetry as evidence and AI output as reasoning assistance. Every material hypothesis should retain supporting evidence, contradicting evidence, confidence, provenance and a human-verification step.

## Recovery verification

Recovery is not considered complete merely because an incident is closed. VEYRA checks open high-risk findings, unexpected services and high-risk flows and presents the result for analyst review. Production deployments should add immutable evidence storage and independent verification.

## Production hardening

Replace POC bearer/admin-token flows with OIDC/SAML, MFA/WebAuthn, short-lived workload identity, signed worker messages, immutable audit storage, tenant isolation, centralized secrets management, and policy-as-code approvals.
