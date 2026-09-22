// Vitest setup — runs before every test file.
import '@testing-library/jest-dom/vitest';

// Some tests touch sessionStorage; ensure it exists in jsdom (it does by
// default, but clear it between test files to avoid cross-test pollution).
beforeEach(() => {
    try {
        sessionStorage.clear();
        localStorage.clear();
    } catch {
        // no-op if storage is unavailable
    }
});