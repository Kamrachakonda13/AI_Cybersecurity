# VEYRA v3.5 Release Notes

## Security Lifecycle

VEYRA now presents one product-wide operating model:

**Discover → Understand → Validate → Investigate → Correlate → Contain → Recover → Prove → Learn → Continuously revalidate.**

## Added

- Security Lifecycle UI.
- Lifecycle overview and plan APIs.
- Ten deterministic lifecycle stages.
- Attention-state calculation from current inventory/evidence.
- Lifecycle governance guardrails.
- Team operating-model documentation.
- 577 individual tool/integration Markdown guides.
- Automated documentation release gate.
- Terminal and UI usage guidance for every registered tool.
- Evidence, remediation, verification and common-mistake guidance for every tool.

## Documentation contract

A registered capability is incomplete if its individual Markdown guide is missing or does not contain the required teaching sections. Run:

```bash
python scripts/validate_tool_documentation.py
```

Expected result: `577 registered`, `577 complete`, `0 missing`, `0 incomplete`.

## Safety

The lifecycle layer is plan-only. It never executes offensive commands or hack-back actions. Actual testing remains behind authorization, scope, Sudo/RBAC, approval, isolated workers and evidence/audit controls.
