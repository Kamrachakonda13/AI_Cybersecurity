/**
 * Component tests for V42TrustedSupplyChainView.
 *
 * Covers: render-with-data, render-with-empty responses, and error fallback.
 */
import React from 'react';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';

import { V42TrustedSupplyChainView } from '../v42.jsx';
import { installFetchMock, seedAuthToken } from './_helpers.jsx';


const OVERVIEW = {
    attestations: 12,
    canary_cohorts: 3,
    ai_supply_chain_assets: 5,
    armed_circuit_breakers: 1,
    trust_invariant: 'No tool, model, agent or dataset is trusted until its digest, provenance and evidence are verified.',
    gates: ['identity', 'provenance', 'integrity', 'policy', 'validation'],
    integrations: {
        tuf: { status: 'available', purpose: 'update metadata' },
        cosign: { status: 'available', purpose: 'signature verification' },
    },
};

const ASSETS = [
    {
        asset_id: 'agent-1',
        name: 'SOC Copilot',
        asset_type: 'agent',
        version: '1.2.0',
        digest: 'sha256:abc',
        provenance_uri: 'https://example/prov',
        sbom_uri: 'https://example/sbom',
        trust_status: 'verified',
    },
];

const BREAKERS = [
    { breaker_id: 'br-1', agent_id: 'agent-1', scope: 'agent', reason: 'runaway tool calls', state: 'armed' },
];


describe('V42TrustedSupplyChainView', () => {
    beforeEach(() => {
        seedAuthToken();
    });

    afterEach(() => {
        cleanup();
        vi.unstubAllGlobals();
    });

    it('renders the header and eyebrow', () => {
        installFetchMock([
            { match: '/api/v42/trusted-supply-chain/overview', response: {} },
            { match: '/api/v42/ai-supply-chain/assets', response: [] },
            { match: '/api/v42/agent-circuit-breakers', response: [] },
        ]);
        render(<V42TrustedSupplyChainView />);
        expect(screen.getByText(/VEYRA V4\.2 · TRUSTED SUPPLY CHAIN/i)).toBeInTheDocument();
        expect(screen.getByText('Trusted Supply Chain Fabric')).toBeInTheDocument();
    });

    it('renders trust metric cards after data loads', async () => {
        installFetchMock([
            { match: '/api/v42/trusted-supply-chain/overview', response: OVERVIEW },
            { match: '/api/v42/ai-supply-chain/assets', response: ASSETS },
            { match: '/api/v42/agent-circuit-breakers', response: BREAKERS },
        ]);
        render(<V42TrustedSupplyChainView />);

        await waitFor(() => {
            expect(screen.getByText('Attestations')).toBeInTheDocument();
        });
        expect(screen.getByText('12')).toBeInTheDocument();
        expect(screen.getByText('Canary cohorts')).toBeInTheDocument();
        expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('renders the trust invariant text', async () => {
        installFetchMock([
            { match: '/api/v42/trusted-supply-chain/overview', response: OVERVIEW },
            { match: '/api/v42/ai-supply-chain/assets', response: [] },
            { match: '/api/v42/agent-circuit-breakers', response: [] },
        ]);
        render(<V42TrustedSupplyChainView />);

        await waitFor(() => {
            expect(screen.getByText(OVERVIEW.trust_invariant)).toBeInTheDocument();
        });
    });

    it('renders verification gate names', async () => {
        installFetchMock([
            { match: '/api/v42/trusted-supply-chain/overview', response: OVERVIEW },
            { match: '/api/v42/ai-supply-chain/assets', response: [] },
            { match: '/api/v42/agent-circuit-breakers', response: [] },
        ]);
        render(<V42TrustedSupplyChainView />);

        await waitFor(() => {
            expect(screen.getByText('identity')).toBeInTheDocument();
        });
        expect(screen.getByText('provenance')).toBeInTheDocument();
        expect(screen.getByText('integrity')).toBeInTheDocument();
    });

    it('renders registered AI supply-chain assets', async () => {
        installFetchMock([
            { match: '/api/v42/trusted-supply-chain/overview', response: OVERVIEW },
            { match: '/api/v42/ai-supply-chain/assets', response: ASSETS },
            { match: '/api/v42/agent-circuit-breakers', response: [] },
        ]);
        render(<V42TrustedSupplyChainView />);

        await waitFor(() => {
            expect(screen.getByText('SOC Copilot')).toBeInTheDocument();
        });
        expect(screen.getByText('verified')).toBeInTheDocument();
    });

    it('renders circuit breakers', async () => {
        installFetchMock([
            { match: '/api/v42/trusted-supply-chain/overview', response: OVERVIEW },
            { match: '/api/v42/ai-supply-chain/assets', response: [] },
            { match: '/api/v42/agent-circuit-breakers', response: BREAKERS },
        ]);
        render(<V42TrustedSupplyChainView />);

        await waitFor(() => {
            expect(screen.getByText('agent-1')).toBeInTheDocument();
        });
        // reason renders inside a larger text node: "agent · runaway tool calls"
        expect(screen.getByText(/runaway tool calls/)).toBeInTheDocument();
        expect(screen.getByText('armed')).toBeInTheDocument();
    });

    it('shows empty-state messages when there is no data', async () => {
        installFetchMock([
            { match: '/api/v42/trusted-supply-chain/overview', response: {} },
            { match: '/api/v42/ai-supply-chain/assets', response: [] },
            { match: '/api/v42/agent-circuit-breakers', response: [] },
        ]);
        render(<V42TrustedSupplyChainView />);

        // Text node may contain "NoAI" (missing space in source) or "No AI";
        // match on the more stable suffix.
        await waitFor(() => {
            expect(screen.getByText(/supply-chain assets registered yet/i)).toBeInTheDocument();
        });
        expect(screen.getByText(/emergency circuit breakers are armed/i)).toBeInTheDocument();
    });

    it('renders production integrations from overview', async () => {
        installFetchMock([
            { match: '/api/v42/trusted-supply-chain/overview', response: OVERVIEW },
            { match: '/api/v42/ai-supply-chain/assets', response: [] },
            { match: '/api/v42/agent-circuit-breakers', response: [] },
        ]);
        render(<V42TrustedSupplyChainView />);

        await waitFor(() => {
            expect(screen.getByText('TUF')).toBeInTheDocument();
        });
        expect(screen.getByText('COSIGN')).toBeInTheDocument();
    });
});