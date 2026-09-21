# VEYRA v3.2 Team Operations Playbook

## Mission
VEYRA is designed so that a team member can understand **why** a tool exists, **when** to use it, **how** to start it safely, **what evidence** to capture and **how** to remediate the result.

## Daily workflow
1. Start from the business/security objective.
2. Open the relevant VEYRA workspace.
3. Read the individual tool help page.
4. Confirm authorization and scope.
5. Choose the least-invasive profile.
6. Use the managed worker or approved connector.
7. Preserve evidence and provenance.
8. Correlate with Security Graph and threat intelligence.
9. Remediate.
10. Verify.

## Role training

### SOC / Blue Team
Focus on Network Defense, DFIR, Endpoint, Identity, Cloud, Threat Intelligence, Detection Engineering and AI Incident Response.

### Red / Purple Team
Focus on Network Discovery, Web/API, AppSec, Wireless, Vulnerability, Exploit Validation and AI/Agent security. Exercises must use authorized scopes or isolated labs.

### AI Security Engineer
Focus on LLM Red Team, LLM Evaluation, Agent Evaluation, MCP, A2A, prompt/context security, memory, RAG, vector stores, model security, adversarial ML, AI supply chain, observability and governance.

### Cloud / Kubernetes
Focus on cloud posture, IAM, containers, Kubernetes, IaC, runtime and software/model supply chain.

### DFIR / Malware
Focus on evidence preservation, memory, disk, network, malware triage, reverse engineering and threat intelligence.

### Security Engineering
Focus on detection engineering, workers, policy, automation, evidence, governance and platform hardening.

## AI security control baseline
VEYRA maps AI work to the current OWASP GenAI 2026 guidance, OWASP Agentic Applications 2026, OWASP Agent Control Standard, NIST AI RMF/GenAI Profile, Google SAIF and MITRE ATLAS. OWASP's 2026 Agent Control Standard emphasizes inspectability, traceability, instrumentation and runtime control for agents.

## Terminal rule
Terminal access is worker-local and policy-bound. Use `--help`/version first, then the exact VEYRA-generated command profile. Never turn the platform into an unrestricted browser shell.

## Incident / adversary trace rule
Preserve evidence first. Correlate network, identity, endpoint, cloud, DNS and threat-intelligence evidence. Build a timeline and confidence-rated hypotheses. Contain the affected environment. Do not hack back.

## Documentation rule
Adding a tool without an individual `docs/tools/<tool>.md` page is an incomplete feature.
