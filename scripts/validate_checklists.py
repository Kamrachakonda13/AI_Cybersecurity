#!/usr/bin/env python3
"""Validate docs/CHECKLISTS.md against checklist_registry.py."""
import re
import sys
sys.path.insert(0, 'backend')
from collections import Counter
from app.services.checklist_registry import CHECKLISTS

with open('docs/CHECKLISTS.md') as f:
    md = f.read()

# total
m = re.search(r"\*\*Total:\*\* (\d+) checklists", md)
if not m:
    print("FAIL: total not found in docs/CHECKLISTS.md")
    sys.exit(1)
md_total = int(m.group(1))
if md_total != len(CHECKLISTS):
    print(f"FAIL: docs total {md_total} != registry {len(CHECKLISTS)}")
    sys.exit(1)

# per-domain counts from markdown table
per_md = {}
for line in md.splitlines():
    if line.startswith("| ") and not line.startswith("| Domain") and not line.startswith("| **Total"):
        parts = [p.strip() for p in line.split("|")]
        # parts[1]=domain, parts[2]=count
        if len(parts) >= 4 and parts[1] in {"live_monitoring","identity","endpoint","network_defense","cloud_container","ai_agent","dfir","governance","supply_chain","red_team","blue_team"}:
            per_md[parts[1]] = int(parts[2])

actual = Counter(c['domain'] for c in CHECKLISTS)
if dict(actual) != per_md:
    print(f"FAIL: per-domain mismatch\n  actual={dict(actual)}\n  md={per_md}")
    sys.exit(1)

# IDs present
md_ids = set(re.findall(r"`([a-z0-9-]+)` \|", md))
reg_ids = {c['id'] for c in CHECKLISTS}
if md_ids != reg_ids:
    print(f"FAIL: id mismatch missing={reg_ids-md_ids} extra={md_ids-reg_ids}")
    sys.exit(1)

print(f"OK: {len(CHECKLISTS)} checklists, {len(actual)} domains, all IDs present")
