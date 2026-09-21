#!/usr/bin/env python3
"""Managed-worker verifier contract for VEYRA v5.0.

This worker intentionally accepts only structured verification requests. It does
not accept shell commands, arbitrary package-manager operations, payloads, C2,
credential attacks, or network attack instructions.
"""
import hashlib, json, sys
ALLOWED={'cosign','syft','grype','tuf-client','spiffe-verifier','aibom-validator','trajectory-validator'}

def verify(req):
    tool=req.get('verifier')
    if tool not in ALLOWED: raise ValueError('verifier not allowlisted')
    subject=req.get('subject_digest','')
    if not subject.startswith('sha256:'): raise ValueError('immutable sha256 subject required')
    result={'contract_version':'5.0','verifier':tool,'subject_digest':subject,'status':'verification_required','evidence_sha256':hashlib.sha256(json.dumps(req,sort_keys=True).encode()).hexdigest(),'execution':'managed_worker_only'}
    return result

if __name__=='__main__': print(json.dumps(verify(json.load(sys.stdin)),indent=2))
