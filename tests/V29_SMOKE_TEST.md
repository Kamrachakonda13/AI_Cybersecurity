# v3.0 smoke validation

Validated with `PYTHONPATH=. python` after `Base.metadata.create_all()`:

- app version reports `3.0.0`.
- all six `/api/v29/*` routes are registered.
- overview, wireless, timeline, infrastructure and attribution service functions execute against an empty database.
- evidence-bundle route is admin gated in the API.

Inherited backend suite at release time: **58 passed / 5 failed**. The five failures are existing shared-DB/order-dependent tests from earlier releases (`discovery`, `intel fusion`, `USB`, `heartbeat`, `triage`); they were not introduced by the v3.0 additions.
