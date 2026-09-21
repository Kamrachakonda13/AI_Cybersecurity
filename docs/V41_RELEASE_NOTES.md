# VEYRA v4.1 Release Notes

## Verified Tool Supply Chain Runtime

- structured managed-worker verification receipts
- immutable artifact digest matching
- eight release health gates
- health evidence SHA-256
- healthy-only release promotion
- canary/stable/extended-stable promotion controller
- automatic rollback planning after failed health/canary validation when an active prior release exists
- stronger enforcement of frozen, pinned and immutable update policies
- production integration contract for TUF, Cosign/Sigstore, Syft, Grype and SLSA v1.2/in-toto

## Security boundary

The control plane does not execute arbitrary shell commands, package managers or downloaded security tools. Artifact verification and binary operations remain in isolated managed workers.
