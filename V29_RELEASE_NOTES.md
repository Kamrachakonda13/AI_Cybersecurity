# VEYRA v3.0.0 Release Notes

## Added
- Adversary Intelligence overview.
- Wireless Defense first-class UI.
- Attack Timeline.
- Infrastructure Investigation.
- Attribution & Evidence workflow.
- v3.0 REST API composition layer.
- Evidence-bundle staging and chain-of-custody guidance.
- v3.0 documentation.

## Security boundary
The new surfaces are defensive investigation and evidence workflows. They do not add hack-back, credential capture, wireless disruption, persistence, C2, or unrestricted shell execution to the SaaS UI/API.

## Validation
- Python compilation: PASS.
- Backend test suite: 58 passed, 5 legacy/order-dependent failures in the inherited suite. No new v3.0 test failures were observed; dedicated v3.0 smoke tests are included in the release validation report.
- Frontend production build was not run in the build environment because the archived `node_modules` was not available and installing dependencies was not reliable. Run `npm ci && npm run build` in `frontend/` before production deployment.
