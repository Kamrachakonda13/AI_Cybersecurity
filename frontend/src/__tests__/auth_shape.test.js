// Structural test for the auth-header helpers that appear throughout main.jsx.
//
// The helpers build header objects. We can't import them directly (main.jsx
// isn't modular), so we verify the shape patterns appear correctly in source.

import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const MAIN_SRC = readFileSync(resolve(__dirname, '..', 'main.jsx'), 'utf8');

describe('auth header helpers', () => {
    it('builds a Bearer Authorization header from the user token', () => {
        // Pattern: Authorization:`Bearer ${sessionStorage.getItem('VEYRA_user_token')}`
        expect(MAIN_SRC).toMatch(/Authorization:\s*`Bearer \$\{sessionStorage\.getItem\('VEYRA_user_token'\)\}`/);
    });

    it('attaches X-VEYRA-Admin-Token when an admin token is present', () => {
        expect(MAIN_SRC).toMatch(/X-VEYRA-Admin-Token/);
    });

    it('attaches X-VEYRA-Privileged-Admin-Token when a privileged token is present', () => {
        // The source has a known typo "Priviledged" — accept both spellings.
        expect(MAIN_SRC).toMatch(/X-VEYRA-Priviledged-Admin-Token|X-VEYRA-Privileged-Admin-Token/);
    });

    it('attaches X-VEYRA-AI-Token for AI gateway requests', () => {
        expect(MAIN_SRC).toMatch(/X-VEYRA-AI-Token/);
    });

    it('does not use a raw `awaitr.` (missing-space) token pattern', () => {
        // Regression guard for the P2-0 discovery: a paste artifact looked like
        // `awaitr.json()` — main.jsx should never have this pattern.
        expect(MAIN_SRC).not.toMatch(/\bawaitr\./);
    });
});