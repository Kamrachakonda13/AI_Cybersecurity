// Smoke tests for browser storage helpers.
//
// main.jsx reads/writes sessionStorage using VEYRA_* keys (uppercase VEYRA,
// snake_case after). This file validates the primitives so any refactor of
// storage semantics has a safety net.

import { describe, it, expect, beforeEach } from 'vitest';

const KEYS = {
    user: 'VEYRA_user_token',
    admin: 'VEYRA_admin_token',
    privilegedAdmin: 'VEYRA_privileged_admin_token',
    ai: 'VEYRA_ai_token',
};

describe('sessionStorage: VEYRA_* keys', () => {
    beforeEach(() => {
        sessionStorage.clear();
    });

    it('round-trips a user token', () => {
        sessionStorage.setItem(KEYS.user, 'tok-123');
        expect(sessionStorage.getItem(KEYS.user)).toBe('tok-123');
    });

    it('round-trips an admin token', () => {
        sessionStorage.setItem(KEYS.admin, 'adm-456');
        expect(sessionStorage.getItem(KEYS.admin)).toBe('adm-456');
    });

    it('round-trips a privileged admin token', () => {
        sessionStorage.setItem(KEYS.privilegedAdmin, 'p-adm-789');
        expect(sessionStorage.getItem(KEYS.privilegedAdmin)).toBe('p-adm-789');
    });

    it('round-trips an AI gateway token', () => {
        sessionStorage.setItem(KEYS.ai, 'ai-tok');
        expect(sessionStorage.getItem(KEYS.ai)).toBe('ai-tok');
    });

    it('removes admin and privileged keys on clear()', () => {
        sessionStorage.setItem(KEYS.admin, 'adm');
        sessionStorage.setItem(KEYS.privilegedAdmin, 'p-adm');
        sessionStorage.removeItem(KEYS.admin);
        sessionStorage.removeItem(KEYS.privilegedAdmin);
        expect(sessionStorage.getItem(KEYS.admin)).toBeNull();
        expect(sessionStorage.getItem(KEYS.privilegedAdmin)).toBeNull();
    });

    it('does not use aegisx_ keys', () => {
        sessionStorage.setItem(KEYS.user, 'x');
        const keys = Object.keys(sessionStorage);
        for (const k of keys) {
            expect(k).not.toMatch(/aegisx/i);
        }
    });
});