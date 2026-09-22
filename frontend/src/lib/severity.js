/**
 * Severity explainer text and helpers.
 *
 * IMPORTANT: These bands MUST match:
 *   - backend/app/services/risk.py:severity
 *   - backend/app/services/teams.py:SEVERITY_PLAYBOOKS
 * All three use ≥80 / ≥60 / ≥35 for CRITICAL / HIGH / MEDIUM.
 */

export const SEV_HELP = {
    CRITICAL: 'CRITICAL (risk ≥ 80): internet-facing + high CVSS and/or CISA KEV + sensitive data or privileged access. Act first — validated exploit path likely exists.',
    HIGH: 'HIGH (risk 60–79): strong risk combo (e.g. exposed service, CVSS 7+, over-privileged identity, public cloud). Fix in this cycle.',
    MEDIUM: 'MEDIUM (risk 35–59): notable weakness without full exploit chain (e.g. missing header, anomalous session). Harden soon.',
    LOW: 'LOW (risk < 35): hygiene issue (banner disclosure, minor misconfig). Fix opportunistically.',
};

export const RISK_FORMULA = 'Risk = criticality×5 + CVSS×5 + exploitability×8 + 15 if exposed + privilege×4 + data-sensitivity×5 + threat×10 + anomaly×8 (capped 100). See backend/app/services/risk.py.';

export function sevHelp(s) {
    return SEV_HELP[s] || SEV_HELP.MEDIUM;
}