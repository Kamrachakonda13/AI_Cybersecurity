# VEYRA v3.3 — Security Readiness Center

## Purpose
The Security Readiness Center turns VEYRA from a tool catalog and team academy into a repeatable operational-readiness system.

## Production readiness domains
1. Identity & Privilege
2. Scope & Authorization
3. Managed Worker
4. Evidence & Provenance
5. AI Runtime Control
6. AI Data Security
7. Software & AI Supply Chain
8. Detection & Response
9. Recovery & Exercises
10. Team Documentation

## Release gate
A release should not be considered production-ready unless:
- every registered tool has an individual Markdown help page;
- privileged actions have explicit scope, approval and audit records;
- managed workers are isolated and version-pinned;
- evidence is normalized and hashed;
- AI agents have identity, capability policy and traceability;
- AI data flows include prompt/context/memory/RAG controls;
- SBOM/AIBOM and provenance are available for relevant artifacts;
- incident exercises produce evidence and recovery verification;
- documentation is validated automatically in CI.

## Defensive exercise model
Use isolated labs or explicitly authorized environments. The platform is designed for detection, validation, evidence collection, containment and recovery verification. It does not provide hack-back or unrestricted offensive execution.

## Current AI baseline
VEYRA maps its AI-security program to the OWASP GenAI LLM Top 10 2026, OWASP Top 10 for Agentic Applications 2026, and the OWASP Agent Control Standard (ACS). ACS emphasizes inspectable, traceable and instrumentable agents with runtime-enforced controls. See the official OWASP resources before updating the control mapping.

NIST AI RMF and the Generative AI Profile remain governance references for trustworthy, secure and resilient AI lifecycle management.
