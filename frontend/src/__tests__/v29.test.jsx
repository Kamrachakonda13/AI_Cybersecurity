/**
 * Component tests for v29.jsx views.
 *
 * Covers: WirelessDefenseView, AdversaryTimelineView,
 * AdversaryInfrastructureView, AttributionView, V29Overview.
 */
import React from 'react';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';

import {
    WirelessDefenseView,
    AdversaryTimelineView,
    AdversaryInfrastructureView,
    AttributionView,
    V29Overview,
} from '../v29.jsx';
import { installFetchMock, seedAuthToken } from './_helpers.jsx';


const WIRELESS = {
    access_points: [
        { id: 1, ssid: 'LabWifi', bssid: 'AA:BB:CC:DD:EE:01', channel: 6, security: 'WPA2', signal_dbm: -55, band: '2.4GHz' },
    ],
    clients: [
        { id: 1, hostname: 'iphone-1', ip_address: '10.0.0.5', mac: 'AA:BB:CC:11:22:33', vendor: 'Apple', trusted: true, last_seen: '2026-09-22T10:00:00Z' },
    ],
    rogue_candidates: [
        { id: 1, subject: 'AA:BB:CC:99:99:99', reason: 'outside trusted baseline' },
    ],
    execution_boundary: 'metadata and evidence workflows only',
};

const TIMELINE = [
    { type: 'network_flow', actor: '10.0.0.5', target: '10.0.0.1:443', time: '2026-09-22T10:00:00Z', detail: 'tcp · 1000 bytes', severity: 'HIGH', risk: 75 },
];

const INFRASTRUCTURE = {
    services: [
        { host: 'web-01', port: 22, protocol: 'tcp', service: 'ssh', process: 'sshd', pid: 101, user: 'root', expected: true },
    ],
    flows: [
        { src: '10.0.0.5', dst: '10.0.0.1', port: 443, bytes_out: 1000, action: 'allowed', risk: 80 },
    ],
    identities: [
        { username: 'alice', type: 'human', privilege: 5, mfa: true, status: 'active' },
    ],
};

const ATTRIBUTION = {
    hypotheses: [
        {
            id: 'hyp-1',
            label: 'Unauthorized device or unregistered asset',
            confidence: 0.65,
            supporting: ['3 device(s) outside trusted baseline'],
            contradicting: ['Unknown status is not proof of compromise'],
            next: 'Validate against router/DHCP inventory.',
        },
    ],
    disclaimer: 'These are investigation hypotheses, not actor identification.',
};

const V29_OVERVIEW = {
    wireless: { access_points: 3, lan_devices: 10, unknown_devices: 2 },
    telemetry: { assets: 10, services: 5, flows: 20, sessions: 3, identities: 4 },
    investigation: { open_incidents: 1, intel_records: 5, audit_events: 50 },
    pipeline: ['observe', 'preserve', 'correlate', 'reconstruct', 'enrich', 'hypothesize', 'verify', 'contain', 'recover'],
};


describe('WirelessDefenseView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => {
        cleanup();
        vi.unstubAllGlobals();
    });

    it('shows a loading indicator initially', () => {
        installFetchMock([{ match: '/api/v29/wireless', response: WIRELESS }]);
        render(<WirelessDefenseView />);
        expect(screen.getByText(/Loading wireless telemetry/i)).toBeInTheDocument();
    });

    it('renders the header', async () => {
        installFetchMock([{ match: '/api/v29/wireless', response: WIRELESS }]);
        render(<WirelessDefenseView />);
        await waitFor(() => {
            expect(screen.getByText('Wireless Security Center')).toBeInTheDocument();
        });
    });

    it('renders access points panel with the SSID', async () => {
        installFetchMock([{ match: '/api/v29/wireless', response: WIRELESS }]);
        render(<WirelessDefenseView />);
        await waitFor(() => {
            expect(screen.getByText('LabWifi')).toBeInTheDocument();
        });
    });

    it('renders wireless client with trusted status', async () => {
        installFetchMock([{ match: '/api/v29/wireless', response: WIRELESS }]);
        render(<WirelessDefenseView />);
        await waitFor(() => {
            expect(screen.getByText('iphone-1')).toBeInTheDocument();
        });
        expect(screen.getByText('TRUSTED')).toBeInTheDocument();
    });

    it('renders rogue candidates', async () => {
        installFetchMock([{ match: '/api/v29/wireless', response: WIRELESS }]);
        render(<WirelessDefenseView />);
        await waitFor(() => {
            expect(screen.getByText('AA:BB:CC:99:99:99')).toBeInTheDocument();
        });
        expect(screen.getByText('REVIEW')).toBeInTheDocument();
    });

    it('renders the execution boundary callout', async () => {
        installFetchMock([{ match: '/api/v29/wireless', response: WIRELESS }]);
        render(<WirelessDefenseView />);
        await waitFor(() => {
            expect(screen.getByText(/metadata and evidence workflows only/i)).toBeInTheDocument();
        });
    });

    it('shows empty states for no candidates', async () => {
        installFetchMock([
            { match: '/api/v29/wireless', response: { access_points: [], clients: [], rogue_candidates: [], execution_boundary: 'x' } },
        ]);
        render(<WirelessDefenseView />);
        await waitFor(() => {
            expect(screen.getByText(/No AP metadata ingested/i)).toBeInTheDocument();
        });
        expect(screen.getByText(/No baseline candidates/i)).toBeInTheDocument();
    });
});


describe('AdversaryTimelineView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => {
        cleanup();
        vi.unstubAllGlobals();
    });

    it('renders header and boundary callout', async () => {
        installFetchMock([{ match: '/api/v29/timeline', response: TIMELINE }]);
        render(<AdversaryTimelineView />);
        await waitFor(() => {
            expect(screen.getByText('Attack Timeline')).toBeInTheDocument();
        });
        expect(screen.getByText(/evidence correlation, not proof of causality/i)).toBeInTheDocument();
    });

    it('renders correlated events', async () => {
        installFetchMock([{ match: '/api/v29/timeline', response: TIMELINE }]);
        render(<AdversaryTimelineView />);
        await waitFor(() => {
            expect(screen.getByText(/NETWORK_FLOW/)).toBeInTheDocument();
        });
        expect(screen.getByText(/HIGH · 75/)).toBeInTheDocument();
    });

    it('shows empty state when there are no events', async () => {
        installFetchMock([{ match: '/api/v29/timeline', response: [] }]);
        render(<AdversaryTimelineView />);
        await waitFor(() => {
            expect(screen.getByText(/No correlated events yet/i)).toBeInTheDocument();
        });
    });
});


describe('AdversaryInfrastructureView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => {
        cleanup();
        vi.unstubAllGlobals();
    });

    it('renders service attribution with BASELINE/DRIFT badge', async () => {
        installFetchMock([{ match: '/api/v29/infrastructure', response: INFRASTRUCTURE }]);
        render(<AdversaryInfrastructureView />);
        await waitFor(() => {
            expect(screen.getByText(/22\/tcp/)).toBeInTheDocument();
        });
        expect(screen.getByText('BASELINE')).toBeInTheDocument();
    });

    it('renders high-risk flows with risk badge', async () => {
        installFetchMock([{ match: '/api/v29/infrastructure', response: INFRASTRUCTURE }]);
        render(<AdversaryInfrastructureView />);
        await waitFor(() => {
            expect(screen.getByText(/10\.0\.0\.5 → 10\.0\.0\.1:443/)).toBeInTheDocument();
        });
        expect(screen.getByText('RISK 80')).toBeInTheDocument();
    });

    it('renders identity exposure with privilege level', async () => {
        installFetchMock([{ match: '/api/v29/infrastructure', response: INFRASTRUCTURE }]);
        render(<AdversaryInfrastructureView />);
        await waitFor(() => {
            expect(screen.getByText('alice')).toBeInTheDocument();
        });
        expect(screen.getByText('P5')).toBeInTheDocument();
    });
});


describe('AttributionView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => {
        cleanup();
        vi.unstubAllGlobals();
    });

    it('renders the "not proof" callout', async () => {
        installFetchMock([{ match: '/api/v29/attribution', response: ATTRIBUTION }]);
        render(<AttributionView />);
        await waitFor(() => {
            expect(screen.getByText(/does not label an attacker/i)).toBeInTheDocument();
        });
    });

    it('renders hypotheses with confidence and evidence', async () => {
        installFetchMock([{ match: '/api/v29/attribution', response: ATTRIBUTION }]);
        render(<AttributionView />);
        await waitFor(() => {
            expect(screen.getByText('Unauthorized device or unregistered asset')).toBeInTheDocument();
        });
        expect(screen.getByText(/Confidence 65%/)).toBeInTheDocument();
        expect(screen.getByText('HYPOTHESIS')).toBeInTheDocument();
    });

    it('renders the Stage evidence bundle button', async () => {
        installFetchMock([{ match: '/api/v29/attribution', response: ATTRIBUTION }]);
        render(<AttributionView />);
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Stage evidence bundle/i })).toBeInTheDocument();
        });
    });
});


describe('V29Overview', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => {
        cleanup();
        vi.unstubAllGlobals();
    });

    it('renders the header title', async () => {
        installFetchMock([{ match: '/api/v29/overview', response: V29_OVERVIEW }]);
        render(<V29Overview />);
        await waitFor(() => {
            expect(screen.getByText(/Adversary Intelligence & Wireless Defense Fabric/)).toBeInTheDocument();
        });
    });

    it('renders KPI tiles with counts from the overview', async () => {
        installFetchMock([{ match: '/api/v29/overview', response: V29_OVERVIEW }]);
        render(<V29Overview />);
        await waitFor(() => {
            expect(screen.getByText('Unknown wireless/LAN')).toBeInTheDocument();
        });
        expect(screen.getByText('High-level services')).toBeInTheDocument();
    });

    it('renders the investigation pipeline steps', async () => {
        installFetchMock([{ match: '/api/v29/overview', response: V29_OVERVIEW }]);
        render(<V29Overview />);
        await waitFor(() => {
            expect(screen.getByText(/observe/)).toBeInTheDocument();
        });
        expect(screen.getByText(/recover/)).toBeInTheDocument();
    });
});