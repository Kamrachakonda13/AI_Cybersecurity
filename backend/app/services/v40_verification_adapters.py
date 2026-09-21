"""Supply-chain verification policy adapters.

The control plane records verification requirements and evidence. Actual artifact
verification should happen in the isolated artifact/worker plane with approved
binaries of TUF/Cosign/Syft/Grype. This module intentionally does not execute shell
commands or download arbitrary artifacts.
"""
from __future__ import annotations
import shutil

ADAPTERS={
    "tuf":{"purpose":"repository metadata, freshness and rollback protection","binary":"tuf"},
    "cosign":{"purpose":"signature and attestation verification","binary":"cosign"},
    "syft":{"purpose":"SBOM generation","binary":"syft"},
    "grype":{"purpose":"vulnerability scanning of artifacts/SBOMs","binary":"grype"},
}

def inventory():
    return [{**v,"adapter":k,"available_on_control_plane":bool(shutil.which(v["binary"])),"execution":"managed verification worker only"} for k,v in ADAPTERS.items()]
