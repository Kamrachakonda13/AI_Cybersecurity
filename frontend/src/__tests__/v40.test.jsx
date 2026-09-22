/**
 * Component tests for v40.jsx — four views:
 *   V40ToolSupplyChainView, V40DocumentationView,
 *   V40AgentSwarmDefenseView, V41SupplyChainRuntimeView.
 */
import React from 'react';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup, fireEvent } from '@testing-library/react';

import {
    V40ToolSupplyChainView,
    V40DocumentationView,
    V40AgentSwarmDefenseView,
    V41SupplyChainRuntimeView,
} from '../v40.jsx';
import { installFetchMock, seedAuthToken } from './_helpers.jsx';


// ========== fixtures ==========

const V40_OVERVIEW = {
    catalog_tools: 587,
    healthy_releases: 42,
    deployments: 12,
    pending_verification: 3,
    failed_or_quarantined: 1,
    channels: ['candidate', 'canary', 'stable'],
};

const V40_SCOUT = {
    results: [
        { tool_id: 'nmap', name: 'Nmap', category: 'Network Discovery', upstream_source: 'kali', installed_version: '7.95', candidate_count: 1, update_status: 'candidate_available' },
        { tool_id: 'tcpdump', name: 'tcpdump', category: 'Network Defense', upstream_source: 'kali', installed_version: '4.99', candidate_count: 0, update_status: 'discovery_required' },
    ],
};

const V40_DEPS = [
    { deployment_id: 'd-1', tool_id: 'nmap', target_version: '7.95', operation: 'deploy', worker_id: 'w-1', manifest_sha256: 'deadbeef'.repeat(8), state: 'planned' },
];

const V40_HEALTH = [
    { check_id: 'h-1', release_id: 'rel-1', worker_id: 'w-1', evidence_sha256: 'cafebabe'.repeat(8), status: 'passed' },
];

const V40_DOCS = {
    items: [
        { title: 'Lab Guide', section: 'Operations', path: 'docs/LAB_GUIDE.md' },
        { title: 'Production Guide', section: 'Operations', path: 'docs/PRODUCTION_GUIDE.md' },
    ],
};

const V40_AGENT_POLICY = {
    policy: {
        egress_mode: 'deny_by_default',
        service_account_velocity_threshold: 120,
        emergency_stop: false,
        website_collaboration_detection: true,
        require_human_approval_for_external_action: true,
    },
};

const V41_RUNTIME = {
    promotion: 'healthy-only',
    rollback: 'immutable prior release',
    artifact_policy: 'digest-pinned',
    verification_checks: ['artifact_digest', 'signature', 'provenance', 'sbom'],
    production_integrations: ['tuf', 'cosign', 'syft', 'grype'],
    execution_boundary: 'Binary execution is isolated to the managed worker.',
};


// ========== V40ToolSupplyChainView ==========

describe('V40ToolSupplyChainView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header and eyebrow', async () => {
        installFetchMock([
            { match: '/api/v40/supply-chain/overview', response: V40_OVERVIEW },
            { match: '/api/v40/update-scout', response: V40_SCOUT },
            { match: '/api/v40/deployments', response: [] },
            { match: '/api/v40/health-checks', response: [] },
        ]);
        render(<V40ToolSupplyChainView />);
        expect(screen.getByText('VEYRA V4.0 · TOOL SUPPLY CHAIN CONTROL PLANE')).toBeInTheDocument();
        expect(screen.getByText('Update Center')).toBeInTheDocument();
    });

    it('renders KPI tiles after data loads', async () => {
        installFetchMock([
            { match: '/api/v40/supply-chain/overview', response: V40_OVERVIEW },
            { match: '/api/v40/update-scout', response: V40_SCOUT },
            { match: '/api/v40/deployments', response: V40_DEPS },
            { match: '/api/v40/health-checks', response: V40_HEALTH },
        ]);
        render(<V40ToolSupplyChainView />);
        await waitFor(() => {
            expect(screen.getByText('Catalog tools')).toBeInTheDocument();
        });
        expect(screen.getByText('587')).toBeInTheDocument();
        expect(screen.getByText('Verified releases')).toBeInTheDocument();
    });

    it('renders the Update Scout list (excluding discovery_required)', async () => {
        installFetchMock([
            { match: '/api/v40/supply-chain/overview', response: V40_OVERVIEW },
            { match: '/api/v40/update-scout', response: V40_SCOUT },
            { match: '/api/v40/deployments', response: [] },
            { match: '/api/v40/health-checks', response: [] },
        ]);
        render(<V40ToolSupplyChainView />);
        await waitFor(() => {
            expect(screen.getByText('Nmap')).toBeInTheDocument();
        });
        // tcpdump is discovery_required → should be filtered out
        expect(screen.queryByText('tcpdump')).not.toBeInTheDocument();
    });

    it('renders deployment history', async () => {
        installFetchMock([
            { match: '/api/v40/supply-chain/overview', response: V40_OVERVIEW },
            { match: '/api/v40/update-scout', response: V40_SCOUT },
            { match: '/api/v40/deployments', response: V40_DEPS },
            { match: '/api/v40/health-checks', response: [] },
        ]);
        render(<V40ToolSupplyChainView />);
        await waitFor(() => {
            expect(screen.getByText(/nmap → 7\.95/)).toBeInTheDocument();
        });
        expect(screen.getByText('planned')).toBeInTheDocument();
    });

    it('renders health-check results', async () => {
        installFetchMock([
            { match: '/api/v40/supply-chain/overview', response: V40_OVERVIEW },
            { match: '/api/v40/update-scout', response: V40_SCOUT },
            { match: '/api/v40/deployments', response: [] },
            { match: '/api/v40/health-checks', response: V40_HEALTH },
        ]);
        render(<V40ToolSupplyChainView />);
        await waitFor(() => {
            expect(screen.getByText('rel-1')).toBeInTheDocument();
        });
        expect(screen.getByText('passed')).toBeInTheDocument();
    });

    it('renders register-release form and freeze/quarantine buttons', async () => {
        installFetchMock([
            { match: '/api/v40/supply-chain/overview', response: V40_OVERVIEW },
            { match: '/api/v40/update-scout', response: V40_SCOUT },
            { match: '/api/v40/deployments', response: [] },
            { match: '/api/v40/health-checks', response: [] },
        ]);
        render(<V40ToolSupplyChainView />);
        expect(screen.getByRole('button', { name: /Verify & register release/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Freeze 24h/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Quarantine/i })).toBeInTheDocument();
    });

    it('renders the supply-chain security model list', async () => {
        installFetchMock([
            { match: '/api/v40/supply-chain/overview', response: V40_OVERVIEW },
            { match: '/api/v40/update-scout', response: V40_SCOUT },
            { match: '/api/v40/deployments', response: [] },
            { match: '/api/v40/health-checks', response: [] },
        ]);
        render(<V40ToolSupplyChainView />);
        expect(screen.getByText(/advisories and upstream release metadata are signals, not trust/i)).toBeInTheDocument();
    });
});


// ========== V40DocumentationView ==========

describe('V40DocumentationView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header', async () => {
        installFetchMock([{ match: '/api/v40/docs/index', response: V40_DOCS }]);
        render(<V40DocumentationView />);
        expect(screen.getByText('Research, architecture & operating knowledge')).toBeInTheDocument();
    });

    it('renders documentation entries after load', async () => {
        installFetchMock([{ match: '/api/v40/docs/index', response: V40_DOCS }]);
        render(<V40DocumentationView />);
        await waitFor(() => {
            expect(screen.getByText('Lab Guide')).toBeInTheDocument();
        });
        expect(screen.getByText('Production Guide')).toBeInTheDocument();
    });

    it('filters documentation via search input', async () => {
        installFetchMock([{ match: '/api/v40/docs/index', response: V40_DOCS }]);
        render(<V40DocumentationView />);
        await waitFor(() => {
            expect(screen.getByText('Lab Guide')).toBeInTheDocument();
        });
        fireEvent.change(screen.getByPlaceholderText(/Search documentation/i), { target: { value: 'production' } });
        await waitFor(() => {
            expect(screen.queryByText('Lab Guide')).not.toBeInTheDocument();
        });
        expect(screen.getByText('Production Guide')).toBeInTheDocument();
    });
});


// ========== V40AgentSwarmDefenseView ==========

describe('V40AgentSwarmDefenseView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header', async () => {
        installFetchMock([
            { match: '/api/v40/agent-swarm/containment', response: V40_AGENT_POLICY },
        ]);
        render(<V40AgentSwarmDefenseView />);
        expect(screen.getByText('Agent Swarm Containment')).toBeInTheDocument();
    });

    it('renders KPI tiles from policy', async () => {
        installFetchMock([
            { match: '/api/v40/agent-swarm/containment', response: V40_AGENT_POLICY },
        ]);
        render(<V40AgentSwarmDefenseView />);
        await waitFor(() => {
            expect(screen.getByText('deny_by_default')).toBeInTheDocument();
        });
        expect(screen.getByText('120')).toBeInTheDocument();
        expect(screen.getByText('READY')).toBeInTheDocument();
    });

    it('renders the Arm emergency stop button when stop is disabled', async () => {
        installFetchMock([
            { match: '/api/v40/agent-swarm/containment', response: V40_AGENT_POLICY },
        ]);
        render(<V40AgentSwarmDefenseView />);
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Arm emergency stop/i })).toBeInTheDocument();
        });
    });

    it('renders swarm-risk simulator with default values', async () => {
        installFetchMock([
            { match: '/api/v40/agent-swarm/containment', response: V40_AGENT_POLICY },
        ]);
        render(<V40AgentSwarmDefenseView />);
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Simulate containment decision/i })).toBeInTheDocument();
        });
    });

    it('renders the defensive lessons table', async () => {
        installFetchMock([
            { match: '/api/v40/agent-swarm/containment', response: V40_AGENT_POLICY },
        ]);
        render(<V40AgentSwarmDefenseView />);
        // Some lesson labels appear both as a table heading and elsewhere; use
        // getAllByText to tolerate duplicates.
        await waitFor(() => {
            expect(screen.getAllByText('Network egress').length).toBeGreaterThan(0);
        });
        expect(screen.getAllByText(/Emergency stop/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/Evidence-first response/i).length).toBeGreaterThan(0);
    });
});

// ========== V41SupplyChainRuntimeView ==========

describe('V41SupplyChainRuntimeView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header', async () => {
        installFetchMock([
            { match: '/api/v41/supply-chain/runtime', response: V41_RUNTIME },
        ]);
        render(<V41SupplyChainRuntimeView />);
        expect(screen.getByText('Supply Chain Runtime')).toBeInTheDocument();
    });

    it('renders runtime policy tiles', async () => {
        installFetchMock([
            { match: '/api/v41/supply-chain/runtime', response: V41_RUNTIME },
        ]);
        render(<V41SupplyChainRuntimeView />);
        await waitFor(() => {
            expect(screen.getByText('healthy-only')).toBeInTheDocument();
        });
        expect(screen.getByText('immutable prior release')).toBeInTheDocument();
        expect(screen.getByText('digest-pinned')).toBeInTheDocument();
    });

    it('renders verification checks', async () => {
        installFetchMock([
            { match: '/api/v41/supply-chain/runtime', response: V41_RUNTIME },
        ]);
        render(<V41SupplyChainRuntimeView />);
        await waitFor(() => {
            expect(screen.getByText('artifact digest')).toBeInTheDocument();
        });
        expect(screen.getByText('signature')).toBeInTheDocument();
        expect(screen.getByText('sbom')).toBeInTheDocument();
    });

    it('renders production integrations', async () => {
        installFetchMock([
            { match: '/api/v41/supply-chain/runtime', response: V41_RUNTIME },
        ]);
        render(<V41SupplyChainRuntimeView />);
        await waitFor(() => {
            expect(screen.getByText('tuf')).toBeInTheDocument();
        });
        expect(screen.getByText('cosign')).toBeInTheDocument();
    });

    it('renders the execution boundary text', async () => {
        installFetchMock([
            { match: '/api/v41/supply-chain/runtime', response: V41_RUNTIME },
        ]);
        render(<V41SupplyChainRuntimeView />);
        await waitFor(() => {
            expect(screen.getByText(/Binary execution is isolated to the managed worker/i)).toBeInTheDocument();
        });
    });
});