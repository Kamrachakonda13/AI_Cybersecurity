# VEYRA Documentation Contract

Documentation is part of the implementation contract.

## Required per-tool content

Every registered VEYRA tool/integration must have one Markdown guide containing:

- What is it?
- Why VEYRA includes it
- When should the team use it?
- VEYRA UI workflow
- Terminal starting point
- Safe workflow
- Evidence to collect
- How to interpret results
- Remediation and verification
- Common mistakes
- Team teaching summary
- Security boundary

## Release gate

Run:

```bash
python scripts/validate_tool_documentation.py
```

A release must not claim documentation completeness unless the validator reports zero missing and zero incomplete guides.

## Updating a tool

When a tool changes, update its guide in the same change. Changes to permissions, worker requirements, UI workflow, evidence schema, installation/provenance or security boundaries must be reflected in the Markdown page.

## Team usability standard

A new team member should be able to answer four questions from the guide without external context:

1. What is this tool for?
2. Where do I use it in VEYRA?
3. What is the safe terminal starting point?
4. What evidence and remediation should I expect?
