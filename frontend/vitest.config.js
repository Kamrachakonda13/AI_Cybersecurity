import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    test: {
        environment: 'jsdom',
        globals: true,
        setupFiles: ['./src/__tests__/setup.js'],
        include: ['src/**/*.{test,spec}.{js,jsx,ts,tsx}'],
        exclude: ['node_modules', 'dist'],
        reporters: ['default'],
        coverage: {
            provider: 'v8',
            enabled: false, // opt-in via `npm run test:coverage`
            reporter: ['text', 'html', 'lcov'],
            include: ['src/**/*.{js,jsx}'],
            exclude: [
                'src/__tests__/**',
                'src/main.jsx', // monolithic entry — not currently unit-tested
                '**/*.config.js',
            ],
            // Don't fail by default — report first, then set thresholds.
            // To enforce a threshold, uncomment:
            // thresholds: { lines: 80, functions: 80, branches: 80, statements: 80 },
        },
    },
});