/**
 * Tests for frontend/src/lib/why.js.
 */
import { describe, it, expect } from 'vitest';
import {
    whyFinding,
    whyIdentity,
    whyCloud,
    whyPort,
    whyFlow,
    whySession,
} from '../lib/why.js';

describe('whyFinding()', () => {
    it('flags CRITICAL severity', () => {
        expect(whyFinding({ severity: 'CRITICAL' }).join(' ')).toMatch(/Score ≥ 80/);
    });

    it('flags CISA KEV', () => {
        expect(whyFinding({ kev: true }).join(' ')).toMatch(/CISA KEV/);
    });

    it('flags internet exposure', () => {
        expect(whyFinding({ exposure: true }).join(' ')).toMatch(/Internet-facing/);
    });

    it('highlights CVSS ≥ 9 as trivial exploit', () => {
        expect(whyFinding({ cvss: 9.5 }).join(' ')).toMatch(/trivially exploitable/);
        expect(whyFinding({ cvss: 7.5 }).join(' ')).toMatch(/high severity vuln/);
    });

    it('flags risk_score ≥ 60', () => {
        expect(whyFinding({ risk_score: 65 }).join(' ')).toMatch(/above HIGH threshold/);
    });

    it('returns baseline reason when nothing matches', () => {
        expect(whyFinding({})).toEqual(['Baseline risk from asset criticality + data sensitivity.']);
    });

    it('combines multiple reasons', () => {
        const r = whyFinding({ severity: 'CRITICAL', kev: true, exposure: true, cvss: 9.8 });
        expect(r.length).toBeGreaterThanOrEqual(4);
    });
});

describe('whyIdentity()', () => {
    it('flags top-privilege P5', () => {
        expect(whyIdentity({ privilege: 5 }).join(' ')).toMatch(/P5/);
    });

    it('flags P4+', () => {
        expect(whyIdentity({ privilege: 4 }).join(' ')).toMatch(/P4\+/);
    });

    it('flags missing MFA', () => {
        expect(whyIdentity({ mfa_enabled: false }).join(' ')).toMatch(/MFA missing/);
    });

    it('flags service accounts', () => {
        expect(whyIdentity({ identity_type: 'service' }).join(' ')).toMatch(/Service account/);
    });

    it('returns baseline for standard accounts', () => {
        expect(whyIdentity({ privilege: 1, mfa_enabled: true, identity_type: 'user' }))
            .toEqual(['Standard privilege, MFA on.']);
    });
});

describe('whyCloud()', () => {
    it('flags public exposure', () => {
        expect(whyCloud({ public_exposure: true }).join(' ')).toMatch(/PUBLIC/);
    });

    it('flags dangerous misconfigurations', () => {
        expect(whyCloud({ misconfiguration: 'admin policy attached' }).join(' ')).toMatch(/Dangerous misconfig/);
        expect(whyCloud({ misconfiguration: 'excessive permissions' }).join(' ')).toMatch(/Dangerous misconfig/);
        expect(whyCloud({ misconfiguration: 'internet-facing bucket' }).join(' ')).toMatch(/Dangerous misconfig/);
    });

    it('flags HIGH-band risk', () => {
        expect(whyCloud({ risk_score: 75 }).join(' ')).toMatch(/HIGH band/);
    });

    it('returns baseline for private + safe resources', () => {
        expect(whyCloud({})).toEqual(['Private + no critical misconfig.']);
    });
});

describe('whyPort()', () => {
    it('flags unexpected services as possible backdoor/drift', () => {
        const r = whyPort({
            expected: false, service: 'ssh', host: 'web-01', port: 22,
            user: 'root', process: 'sshd', pid: 101,
        });
        expect(r[0]).toMatch(/UNEXPECTED/);
        expect(r[0]).toMatch(/backdoor|drift/);
    });

    it('confirms expected baseline services', () => {
        const r = whyPort({ expected: true, service: 'http', port: 80 });
        expect(r[0]).toMatch(/Expected baseline/);
    });
});

describe('whyFlow()', () => {
    it('flags risk ≥ 70 as possible exfil', () => {
        const r = whyFlow({ risk_score: 75, bytes_out: 1000000, dst_ip: '1.2.3.4', dst_port: 443 });
        expect(r[0]).toMatch(/≥ 70/);
        expect(r[0]).toMatch(/exfil|lateral/);
    });

    it('flags risk 50-69 as elevated', () => {
        expect(whyFlow({ risk_score: 55 })[0]).toMatch(/elevated/);
    });

    it('returns normal for low-risk flows', () => {
        expect(whyFlow({ risk_score: 10 })).toEqual(['Normal volume/destination.']);
    });
});

describe('whySession()', () => {
    it('flags privileged sessions', () => {
        expect(whySession({ privileged: true }).join(' ')).toMatch(/PRIVILEGED session/);
    });

    it('flags anomaly_score ≥ 0.7', () => {
        const r = whySession({ anomaly_score: 0.8, username: 'alice' });
        expect(r.join(' ')).toMatch(/Anomaly 0.8/);
        expect(r.join(' ')).toMatch(/alice/);
    });

    it('flags weak auth methods', () => {
        expect(whySession({ auth_method: 'token' }).join(' ')).toMatch(/Weak auth: token/);
        expect(whySession({ auth_method: 'password-spray' }).join(' ')).toMatch(/Weak auth/);
    });

    it('returns baseline for normal sessions', () => {
        expect(whySession({})).toEqual(['Normal auth context.']);
    });

    it('combines multiple reasons', () => {
        const r = whySession({ privileged: true, anomaly_score: 0.9, auth_method: 'token', username: 'bob' });
        expect(r.length).toBeGreaterThanOrEqual(3);
    });
});