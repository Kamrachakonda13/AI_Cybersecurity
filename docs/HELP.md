# VEYRA Help Guide

## Overview

VEYRA is a security operations control plane. Use the Overview to identify
critical findings, exposed assets, privileged identities, cloud exposure and
AI assets.

## Network

**Ports & Services** answers: what is listening, which process owns it, which
user owns that process, and whether it matches the expected baseline.

**Flows** shows observed source/destination communication. High-risk flows are
signals for investigation, not proof of compromise.

**DNS** is metadata-only in the current design. It does not inspect page
content.

## Identity

Use Identity and Sessions to correlate user → device → source IP → application
→ session → target asset. Review privileged sessions and MFA gaps first.

## Security Graph

The graph connects technical evidence so analysts can investigate attack paths
instead of looking at isolated alerts.

## Forensics

Upload a copy of an artifact for static analysis. The API hashes and parses the
sample but does not execute it.

## Threat Intelligence

CISA KEV identifies known exploited vulnerabilities. NVD provides vulnerability
details. Threat intelligence enriches evidence; it does not automatically prove
that an asset is compromised.

## AI Security

AI Security covers models, agents, tools, memory, RAG and vector stores. Test
against a lab gateway before connecting a production AI system.

## RAG

RAG answers should be grounded in authorized evidence. The future RAG pipeline
uses authorization → hybrid retrieval → reranking → graph context → cited
answer → audit.

## Red Team

Red Team is for authorized simulation in a lab/cyber-range. Use findings to
improve Blue Team detections.

## Blue Team

Blue Team focuses on detection, investigation, containment, remediation and
verification.

## SOAR

SOAR runs begin as `pending_approval`. High-impact actions must not execute
without the appropriate human approval.

## Active attack

When an incident is active:

1. Preserve logs and evidence.
2. Scope affected identities, devices and assets.
3. Build the timeline.
4. Extract IOCs.
5. Enrich with threat intelligence.
6. Map behavior to ATT&CK/ATLAS.
7. Determine likely attack path.
8. Contain using an approved playbook.
9. Eradicate and recover.
10. Re-scan and verify.

Do not retaliate or "hack back".

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
