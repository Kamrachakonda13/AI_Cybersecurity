/**
 * Per-row "why flagged" rationale helpers.
 *
 * Each helper takes a row-shaped object and returns an array of human-readable
 * reasons. Used inline in tables and inside `DetailModal`.
 */

export function whyFinding(f) {
    const r = [];
    if (f.severity === 'CRITICAL') r.push('Score ≥ 80: combined worst factors.');
    if (f.kev) r.push('CISA KEV: actively exploited in the wild.');
    if (f.exposure) r.push('Internet-facing: reachable without prior foothold.');
    if ((f.cvss || 0) >= 9) r.push(`CVSS ${f.cvss}: trivially exploitable, full impact.`);
    else if ((f.cvss || 0) >= 7) r.push(`CVSS ${f.cvss}: high severity vuln.`);
    if ((f.risk_score || 0) >= 60) r.push(`Risk ${f.risk_score}: above HIGH threshold.`);
    if (!r.length) r.push('Baseline risk from asset criticality + data sensitivity.');
    return r;
}

export function whyIdentity(x) {
    const r = [];
    if (x.privilege >= 5) r.push('P5: top privilege — full control if compromised.');
    else if (x.privilege >= 4) r.push('P4+: can reach sensitive workloads.');
    if (!x.mfa_enabled) r.push('MFA missing: single factor = easy takeover.');
    if (x.identity_type === 'service') r.push('Service account: non-human, often over-scoped, no MFA.');
    return r.length ? r : ['Standard privilege, MFA on.'];
}

export function whyCloud(c) {
    const r = [];
    if (c.public_exposure) r.push('PUBLIC: reachable from internet.');
    if (/admin|excessive|internet-facing/i.test(c.misconfiguration || '')) r.push(`Dangerous misconfig: ${c.misconfiguration}.`);
    if ((c.risk_score || 0) >= 60) r.push(`Risk ${c.risk_score}: HIGH band.`);
    return r.length ? r : ['Private + no critical misconfig.'];
}

export function whyPort(p) {
    if (!p.expected) {
        return [`UNEXPECTED ${p.service} on ${p.host}:${p.port} — owned by ${p.user} via ${p.process} (PID ${p.pid}). Not in baseline: possible backdoor or drift.`];
    }
    return [`Expected baseline service ${p.service} on ${p.port}.`];
}

export function whyFlow(f) {
    if (f.risk_score >= 70) {
        return [`Risk ${f.risk_score} ≥ 70: large/rare transfer (${f.bytes_out} bytes) to ${f.dst_ip}:${f.dst_port}. Possible exfil/lateral movement.`];
    }
    if (f.risk_score >= 50) {
        return [`Risk ${f.risk_score}: elevated volume/destination. Review.`];
    }
    return ['Normal volume/destination.'];
}

export function whySession(s) {
    const r = [];
    if (s.privileged) r.push('PRIVILEGED session: can change security state.');
    if (s.anomaly_score >= 0.7) r.push(`Anomaly ${s.anomaly_score}: unusual host/app/auth for ${s.username}.`);
    if (/token|password-spray/i.test(s.auth_method || '')) r.push(`Weak auth: ${s.auth_method}.`);
    return r.length ? r : ['Normal auth context.'];
}