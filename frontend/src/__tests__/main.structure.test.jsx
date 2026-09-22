// Structural smoke tests for main.jsx.
//
// main.jsx is a large single-file React module that renders on import via
// createRoot. We do NOT import it directly (that would mount the app and fire
// 18 fetch calls). Instead, we inspect its source text for critical invariants.
//
// These tests are intentionally structural — they guard against regressions in
// the branding, storage keys, and API URL configuration that P0/P1 changed.

import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const MAIN_SRC = readFileSync(resolve(__dirname, '..', 'main.jsx'), 'utf8');

describe('main.jsx structural invariants', () => {
    it('uses the VEYRA brand, never AegisX', () => {
        expect(MAIN_SRC).not.toMatch(/AegisX/i);
        expect(MAIN_SRC).not.toMatch(/AEGISX/);
    });

    it('uses VEYRA_* sessionStorage keys, never aegisx_*', () => {
        expect(MAIN_SRC).not.toMatch(/aegisx_/i);
        // Every sessionStorage key reference should be VEYRA_*
        const storageRefs = MAIN_SRC.match(/sessionStorage\.(getItem|setItem|removeItem)\(['"`]([^'"`]+)['"`]/g) || [];
        expect(storageRefs.length).toBeGreaterThan(0);
        for (const ref of storageRefs) {
            expect(ref).toMatch(/VEYRA_/);
        }
    });

    it('uses X-VEYRA-* admin headers, never X-AEGISX-*', () => {
        expect(MAIN_SRC).not.toMatch(/X-AEGISX/i);
        expect(MAIN_SRC).toMatch(/X-VEYRA-Admin-Token/);
        expect(MAIN_SRC).toMatch(/X-VEYRA-Privileged-Admin-Token/);
    });

    it('does not contain stray double closing parens in the nav array', () => {
        // Regression guard for the P2-0 fix (extra "))" broke the build).
        expect(MAIN_SRC).not.toMatch(/\],\s*'VEYRA v5 Control Plane',\s*ShieldCheck\]\]\)\)/);
    });

    it('declares a nav array with the VEYRA v5 Control Plane section', () => {
        // nav extracted to lib/nav.js in P7 — main.jsx imports NAV
        const navSrc = readFileSync(resolve(__dirname, '..', 'lib', 'nav.js'), 'utf8');
        expect(MAIN_SRC).toMatch(/NAV/);
        expect(navSrc).toMatch(/'VEYRA v5 Control Plane'/);
        expect(navSrc).toMatch(/Checklist Library/);
        expect(navSrc).toMatch(/Domains & Tools/);
        expect(navSrc).toMatch(/Agents/);
    });

    it('declares the API base from VITE_API_URL or localhost', () => {
        expect(MAIN_SRC).toMatch(/VITE_API_URL|localhost:8000/);
    });
});