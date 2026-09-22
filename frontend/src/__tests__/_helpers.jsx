/**
 * Shared test helpers for rendering VEYRA view components.
 *
 * Every component fetches on mount. We replace global.fetch with a deterministic
 * stub so tests are hermetic and fast.
 */
import { vi } from 'vitest';

/**
 * Install a mock fetch that dispatches by URL substring.
 *
 * @param {Array<{match: string|RegExp, response: any, status?: number}>} routes
 *   Each route matches against the request URL. First match wins.
 * @param {any} fallback  Response for unmatched URLs (default: [] with status 200)
 */
export function installFetchMock(routes, fallback = { body: [], status: 200 }) {
    const mock = vi.fn(async (url) => {
        const u = String(url);
        for (const r of routes) {
            const matched =
                typeof r.match === 'string' ? u.includes(r.match) : r.match.test(u);
            if (matched) {
                const status = r.status ?? 200;
                return {
                    ok: status >= 200 && status < 300,
                    status,
                    json: async () => r.response,
                };
            }
        }
        const status = fallback.status ?? 200;
        return {
            ok: status >= 200 && status < 300,
            status,
            json: async () => fallback.body,
        };
    });
    vi.stubGlobal('fetch', mock);
    return mock;
}

/**
 * Pre-populate sessionStorage with a fake auth token so `auth()` returns a
 * Bearer header without polluting other state.
 */
export function seedAuthToken(token = 'test-token') {
    sessionStorage.setItem('VEYRA_user_token', token);
}