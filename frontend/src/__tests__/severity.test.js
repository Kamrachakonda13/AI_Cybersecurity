/**
 * Tests for frontend/src/lib/severity.js.
 */
import { describe, it, expect } from 'vitest';
import { SEV_HELP, RISK_FORMULA, sevHelp } from '../lib/severity.js';

describe('SEV_HELP', () => {
    it('has entries for all four severity bands', () => {
        expect(Object.keys(SEV_HELP).sort()).toEqual(['CRITICAL', 'HIGH', 'LOW', 'MEDIUM']);
    });

    it('bands match the backend (≥80 / ≥60 / ≥35)', () => {
        expect(SEV_HELP.CRITICAL).toContain('80');
        expect(SEV_HELP.HIGH).toContain('60');
        expect(SEV_HELP.MEDIUM).toContain('35');
    });

    it('each band describes its range', () => {
        expect(SEV_HELP.CRITICAL).toMatch(/≥ 80/);
        expect(SEV_HELP.LOW).toMatch(/< 35/);
    });
});

describe('RISK_FORMULA', () => {
    it('is a non-empty string', () => {
        expect(typeof RISK_FORMULA).toBe('string');
        expect(RISK_FORMULA.length).toBeGreaterThan(40);
    });

    it('references the backend service', () => {
        expect(RISK_FORMULA).toMatch(/risk\.py/);
    });
});

describe('sevHelp()', () => {
    it('returns the matching band text', () => {
        expect(sevHelp('CRITICAL')).toBe(SEV_HELP.CRITICAL);
        expect(sevHelp('HIGH')).toBe(SEV_HELP.HIGH);
        expect(sevHelp('MEDIUM')).toBe(SEV_HELP.MEDIUM);
        expect(sevHelp('LOW')).toBe(SEV_HELP.LOW);
    });

    it('falls back to MEDIUM for unknown severity', () => {
        expect(sevHelp('UNKNOWN')).toBe(SEV_HELP.MEDIUM);
        expect(sevHelp(undefined)).toBe(SEV_HELP.MEDIUM);
        expect(sevHelp(null)).toBe(SEV_HELP.MEDIUM);
        expect(sevHelp('')).toBe(SEV_HELP.MEDIUM);
    });
});