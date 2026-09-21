# VEYRA Incident Reverse-Engineering Workbench

When an active intrusion is suspected, the objective is to determine what
happened and who/what is responsible **without contaminating evidence or
retaliating**.

## Investigation pipeline

```text
Alert
 ↓
Evidence preservation
 ↓
Host / identity / network scope
 ↓
Timeline reconstruction
 ↓
Artifact triage
 ↓
IOC extraction
 ↓
Threat-intelligence enrichment
 ↓
ATT&CK / ATLAS mapping
 ↓
Security Graph correlation
 ↓
Attribution hypotheses
 ↓
Containment approval
 ↓
Recovery + verification
```

## Evidence types

- endpoint process trees
- authentication events
- network flows
- DNS
- HTTP/TLS metadata
- PCAP
- files and hashes
- email artifacts
- cloud audit events
- container/Kubernetes events
- AI/agent traces
- vector retrieval events
- IAM activity
- firewall/WAF/EDR alerts

## Attribution model

VEYRA should never say "this person is the attacker" from one IOC.

Instead maintain:

```text
Hypothesis
  ├── confidence
  ├── supporting evidence[]
  ├── contradicting evidence[]
  ├── first_seen
  ├── last_seen
  ├── infrastructure relationships
  ├── ATT&CK behavior
  └── analyst assessment
```

Possible attribution dimensions:

- infrastructure reuse
- domains/IPs/ASNs
- malware/tooling characteristics
- timestamps/time zones
- TTP sequence
- identity compromise path
- victimology
- known threat-intelligence relationships

## Evidence chain

Every artifact should have:

```text
artifact_id
sha256
source
collector
collected_at
original_timestamp
case_id
custodian
classification
parser_version
analysis_version
```

## Reverse-engineering workbench

VEYRA should orchestrate, but not execute samples in the API process.

Safe API-side analysis:
- hash
- file-type detection
- strings
- metadata
- static IOC extraction
- PCAP metadata
- email parsing
- Office/PDF structure
- PE/ELF header information

Isolated analyst/sandbox layer:
- Ghidra/radare2/IDA
- YARA/ClamAV
- Volatility
- Autopsy/Sleuth Kit
- dynamic malware sandbox
- detonation environment

## Containment

Containment actions should be approval-gated and auditable:
- isolate endpoint
- revoke sessions
- disable compromised identity
- block indicator
- quarantine workload
- restrict cloud exposure

Never delete logs or evidence as part of containment.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
