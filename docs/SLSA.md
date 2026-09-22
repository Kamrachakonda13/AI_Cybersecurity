# SLSA Provenance

VEYRA publishes **SLSA Level 3** provenance attestations for release artifacts.
This document explains what SLSA is, how VEYRA implements it, and how to verify
an artifact's provenance.

## What is SLSA?

**SLSA** (Supply-chain Levels for Software Artifacts) is a security framework
that verifies artifacts haven't been tampered with and records *how* they were
built. It defines four levels:

| Level | Protects against | How |
|---|---|---|
| **1** | Accidental tampering | Documents how the artifact was built |
| **2** | Tampering by a compromised build platform | Signed provenance from a hosted CI |
| **3** | Tampering across the supply chain | Hardened, isolated builds + signed provenance |
| **4** | Insider threats in the build pipeline | Two-party review + hermetic builds |

**VEYRA targets SLSA Level 3** using GitHub's official
[`slsa-framework/slsa-github-generator`](https://github.com/slsa-framework/slsa-github-generator).

## What gets attested

Every VEYRA release tagged `v*` (or a manual `workflow_dispatch` run) produces:

| Artifact | Contents | Purpose |
|---|---|---|
| `veyra-v5.0-<ref>.tar.gz` | Frontend `dist/`, backend source, worker source, tool docs, requirements + lockfile, README | The distributable bundle |
| `veyra-v5.0.sha256` | SHA-256 of the tarball | Integrity check |
| `veyra-v5.0.intoto.jsonl` | SLSA Level 3 provenance attestation | Cryptographic proof of build |

The provenance is signed by GitHub's OIDC issuer and includes:
- The source repository (`github.com/Kamrachakonda13/veyra`)
- The exact commit SHA
- The workflow that built the artifact
- The GitHub Actions runner identity
- SHA-256 hashes of every input artifact

## How to verify

Consumers can verify any VEYRA release artifact using the
[`slsa-verifier`](https://github.com/slsa-framework/slsa-verifier) tool:

```bash
# Install slsa-verifier
go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

# Download the artifact + provenance
gh release download v5.0 --pattern 'veyra-v5.0-*'

# Verify
slsa-verifier verify-artifact veyra-v5.0-v5.0.tar.gz \
  --provenance-path veyra-v5.0.intoto.jsonl \
  --source-uri github.com/Kamrachakonda13/veyra