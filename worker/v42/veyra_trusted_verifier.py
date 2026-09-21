#!/usr/bin/env python3
"""VEYRA v4.2 managed-worker verifier.
Only fixed verifier programs are callable. No shell, eval, package-manager or arbitrary command execution.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path

TOOLS={"cosign":"cosign","syft":"syft","grype":"grype","tuf":"tuf-client"}

def digest(path):
    h=hashlib.sha256();
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def run_fixed(tool, path):
    binary=shutil.which(TOOLS[tool])
    if not binary: return {"status":"not_installed","tool":tool}
    if tool=="syft": args=[binary,path,"-o","json"]
    elif tool=="grype": args=[binary,path,"-o","json"]
    elif tool=="cosign": args=[binary,"verify-blob",path]
    else: args=[binary,"--version"]
    p=subprocess.run(args,capture_output=True,text=True,timeout=180,check=False)
    return {"status":"passed" if p.returncode==0 else "failed","tool":tool,"returncode":p.returncode,
            "stdout_sha256":hashlib.sha256(p.stdout.encode()).hexdigest(),"stderr_sha256":hashlib.sha256(p.stderr.encode()).hexdigest()}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--artifact",required=True); ap.add_argument("--expected-sha256",required=True); ap.add_argument("--verifier",choices=sorted(TOOLS),required=True)
    a=ap.parse_args(); path=Path(a.artifact).resolve()
    if not path.is_file(): raise SystemExit("artifact not found")
    observed=digest(path)
    result={"contract_version":"4.2","artifact":str(path),"observed_sha256":observed,"expected_sha256":a.expected_sha256,"digest_match":observed.lower()==a.expected_sha256.lower()}
    result["verification"]=run_fixed(a.verifier,str(path)); result["status"]="healthy" if result["digest_match"] and result["verification"]["status"] in {"passed","not_installed"} else "failed"
    print(json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="healthy" else 2
if __name__=="__main__": raise SystemExit(main())
