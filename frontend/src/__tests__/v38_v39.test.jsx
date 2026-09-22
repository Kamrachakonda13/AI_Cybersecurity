/**
 * Component tests for v38.jsx (Posture Time Machine) and v39.jsx
 * (Autonomous Exposure Validation / Research Lab).
 */
import React from 'react';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup, fireEvent } from '@testing-library/react';

import { V38PostureTimeMachineView } from '../v38.jsx';
import { V39AutonomousExposureValidationView } from '../v39.jsx';
import { installFetchMock, seedAuthToken } from './_helpers.jsx';


// ========== V38 fixtures ==========

const V38_CURRENT = {
    current: { posture_score: 82, risk_score: 24 },
    inventory: { counts: { ai_assets: 7, assets: 20, identities: 5 } },
};

const V38_HISTORY = {
    snapshots: [
        { snapshot_id: 'snap-1', captured_at: '2026-09-22T10:00:00Z', hash_sha256: 'deadbeef'.repeat(8), posture_score: 91 },
        { snapshot_id: 'snap-2', captured_at: '2026-09-21T10:00:00Z', hash_sha256: 'cafebabe'.repeat(8), posture_score: 74 },
    ],
};

const V38_DRIFT = {
    drift: {
        status: 'changes_detected',
        changes: [
            { target: 'alice', category: 'identity', change_type: 'privilege_escalation', summary: 'Alice gained sudo rights', severity: 'HIGH' },
            { target: 'web-01', category: 'asset', change_type: 'new_port', summary: 'Port 8443 opened', severity: 'MEDIUM' },
        ],
    },
};

const V38_RADAR = {
    providers: [
        { id: 'openai', provider: 'OpenAI', release: 'GPT-X', status: 'released', security_signal: 'No known critical', maps_to: ['AI supply chain'] },
    ],
    endpoint_platforms: [
        { platform: 'windows', release: 'Windows 11 24H2', status: 'patched', source: 'Microsoft', signal: 'Latest cumulative available' },
    ],
};


// ========== V39 fixtures ==========

const V39_OVERVIEW = {
    risk_summary: { critical_agent_candidates: 2, vulnerable_endpoints: 5 },
    counts: { agent_events: 42 },
    rogue_agent_candidates: [
        {
            agent_id: 'suspicious-agent-1',
            events: 12,
            first_seen: '2026-09-21T10:00:00Z',
            last_seen: '2026-09-22T15:00:00Z',
            score: 78,
            reasons: ['Unknown tool call', 'External destination', 'No provenance record'],
        },
    ],
    endpoint_exposure: [
        { hostname: 'web-01', os: 'Ubuntu 22.04', ip: '10.0.0.5', last_seen: '2026-09-22T10:00:00Z', critical: 2, kev: 1 },
    ],
    identity_anomalies: [
        { username: 'alice', source_ip: '203.0.113.5', asset_id: 'web-01', application: 'sso', anomaly_score: 0.82 },
    ],
};

const V39_CASES = {
    cases: [
        { case_id: 'case-1', agent_id: 'suspicious-agent-1', status: 'investigating' },
    ],
};

const V39_INVESTIGATION = {
    case_id: 'case-42',
    confidence: 0.78,
    evidence_sha256: 'deadbeef'.repeat(8),
    root_cause: 'Unknown agent invoked an unapproved tool with external egress.',
    timeline: [
        { operation: 'invoke_agent', tool: 'shell_exec', created_at: '2026-09-22T14:00:00Z', trace_id: 'trace-1', risk: 85 },
    ],
    containment_plan: [
        { step: 'revoke_credentials', action: 'revoke_credentials', detail: 'Revoke agent identity and session tokens.' },
        { step: 'isolate_agent', action: 'isolate_agent', detail: 'Isolate endpoint hosting the agent.' },
    ],
};


// ========== V38PostureTimeMachineView ==========

describe('V38PostureTimeMachineView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header and eyebrow', async () => {
        installFetchMock([
            { match: '/api/v38/posture/current', response: V38_CURRENT },
            { match: '/api/v38/posture/history', response: V38_HISTORY },
            { match: '/api/v38/posture/drift', response: V38_DRIFT },
            { match: '/api/v38/ai-endpoint-radar', response: V38_RADAR },
        ]);
        render(<V38PostureTimeMachineView />);
        expect(screen.getByText('VEYRA V3.8 · POSTURE + AI/ENDPOINT INTELLIGENCE')).toBeInTheDocument();
        expect(screen.getByText('Security Posture Time Machine')).toBeInTheDocument();
    });

    it('renders KPI tiles after data loads', async () => {
        installFetchMock([
            { match: '/api/v38/posture/current', response: V38_CURRENT },
            { match: '/api/v38/posture/history', response: V38_HISTORY },
            { match: '/api/v38/posture/drift', response: V38_DRIFT },
            { match: '/api/v38/ai-endpoint-radar', response: V38_RADAR },
        ]);
        render(<V38PostureTimeMachineView />);
        await waitFor(() => {
            expect(screen.getByText('POSTURE SCORE')).toBeInTheDocument();
        });
        expect(screen.getByText('82')).toBeInTheDocument();
        expect(screen.getByText('RISK SCORE')).toBeInTheDocument();
        expect(screen.getByText('24')).toBeInTheDocument();
    });

    it('renders posture history snapshots', async () => {
        installFetchMock([
            { match: '/api/v38/posture/current', response: V38_CURRENT },
            { match: '/api/v38/posture/history', response: V38_HISTORY },
            { match: '/api/v38/posture/drift', response: V38_DRIFT },
            { match: '/api/v38/ai-endpoint-radar', response: V38_RADAR },
        ]);
        render(<V38PostureTimeMachineView />);
        await waitFor(() => {
            expect(screen.getByText('snap-1')).toBeInTheDocument();
        });
        expect(screen.getByText('snap-2')).toBeInTheDocument();
    });

    it('renders drift changes with severity badges', async () => {
        installFetchMock([
            { match: '/api/v38/posture/current', response: V38_CURRENT },
            { match: '/api/v38/posture/history', response: V38_HISTORY },
            { match: '/api/v38/posture/drift', response: V38_DRIFT },
            { match: '/api/v38/ai-endpoint-radar', response: V38_RADAR },
        ]);
        render(<V38PostureTimeMachineView />);
        await waitFor(() => {
            expect(screen.getByText('alice')).toBeInTheDocument();
        });
        expect(screen.getAllByText('HIGH').length).toBeGreaterThan(0);
        expect(screen.getByText(/Alice gained sudo rights/)).toBeInTheDocument();
    });

    it('renders AI provider radar', async () => {
        installFetchMock([
            { match: '/api/v38/posture/current', response: V38_CURRENT },
            { match: '/api/v38/posture/history', response: V38_HISTORY },
            { match: '/api/v38/posture/drift', response: V38_DRIFT },
            { match: '/api/v38/ai-endpoint-radar', response: V38_RADAR },
        ]);
        render(<V38PostureTimeMachineView />);
        await waitFor(() => {
            expect(screen.getByText(/OpenAI — GPT-X/)).toBeInTheDocument();
        });
    });

    it('renders endpoint platform radar', async () => {
        installFetchMock([
            { match: '/api/v38/posture/current', response: V38_CURRENT },
            { match: '/api/v38/posture/history', response: V38_HISTORY },
            { match: '/api/v38/posture/drift', response: V38_DRIFT },
            { match: '/api/v38/ai-endpoint-radar', response: V38_RADAR },
        ]);
        render(<V38PostureTimeMachineView />);
        await waitFor(() => {
            expect(screen.getByText(/windows — Windows 11 24H2/)).toBeInTheDocument();
        });
    });

    it('renders the Capture snapshot button', async () => {
        installFetchMock([
            { match: '/api/v38/posture/current', response: V38_CURRENT },
            { match: '/api/v38/posture/history', response: V38_HISTORY },
            { match: '/api/v38/posture/drift', response: V38_DRIFT },
            { match: '/api/v38/ai-endpoint-radar', response: V38_RADAR },
        ]);
        render(<V38PostureTimeMachineView />);
        expect(screen.getByRole('button', { name: /Capture snapshot/i })).toBeInTheDocument();
    });

    it('shows empty state when no snapshots exist', async () => {
        installFetchMock([
            { match: '/api/v38/posture/current', response: V38_CURRENT },
            { match: '/api/v38/posture/history', response: { snapshots: [] } },
            { match: '/api/v38/posture/drift', response: { drift: { changes: [] } } },
            { match: '/api/v38/ai-endpoint-radar', response: { providers: [], endpoint_platforms: [] } },
        ]);
        render(<V38PostureTimeMachineView />);
        await waitFor(() => {
            expect(screen.getByText(/No snapshots yet/i)).toBeInTheDocument();
        });
    });

    it('renders the security boundary callout', async () => {
        installFetchMock([
            { match: '/api/v38/posture/current', response: V38_CURRENT },
            { match: '/api/v38/posture/history', response: V38_HISTORY },
            { match: '/api/v38/posture/drift', response: V38_DRIFT },
            { match: '/api/v38/ai-endpoint-radar', response: V38_RADAR },
        ]);
        render(<V38PostureTimeMachineView />);
        expect(screen.getByText(/does not infer that a host is vulnerable merely because it runs a named OS/i)).toBeInTheDocument();
    });
});


// ========== V39AutonomousExposureValidationView ==========

describe('V39AutonomousExposureValidationView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header and eyebrow', async () => {
        installFetchMock([
            { match: '/api/v39/exposure/overview', response: V39_OVERVIEW },
            { match: '/api/v39/rogue-agents/cases', response: V39_CASES },
        ]);
        render(<V39AutonomousExposureValidationView />);
        expect(screen.getByText('VEYRA V3.9 · AUTONOMOUS EXPOSURE VALIDATION FABRIC')).toBeInTheDocument();
        expect(screen.getByText('AI Security Research Lab')).toBeInTheDocument();
    });

    it('renders KPI tiles from risk_summary', async () => {
        installFetchMock([
            { match: '/api/v39/exposure/overview', response: V39_OVERVIEW },
            { match: '/api/v39/rogue-agents/cases', response: V39_CASES },
        ]);
        render(<V39AutonomousExposureValidationView />);
        await waitFor(() => {
            expect(screen.getByText('ROGUE AGENT CANDIDATES')).toBeInTheDocument();
        });
        expect(screen.getByText('2')).toBeInTheDocument();
        expect(screen.getByText('VULNERABLE ENDPOINTS')).toBeInTheDocument();
        expect(screen.getByText('5')).toBeInTheDocument();
    });

    it('renders rogue agent candidates with scores and reasons', async () => {
        installFetchMock([
            { match: '/api/v39/exposure/overview', response: V39_OVERVIEW },
            { match: '/api/v39/rogue-agents/cases', response: V39_CASES },
        ]);
        render(<V39AutonomousExposureValidationView />);
        await waitFor(() => {
            expect(screen.getByText('suspicious-agent-1')).toBeInTheDocument();
        });
        expect(screen.getByText('78/100')).toBeInTheDocument();
        expect(screen.getByText(/Unknown tool call/)).toBeInTheDocument();
    });

    it('renders endpoint exposure with critical/KEV badge', async () => {
        installFetchMock([
            { match: '/api/v39/exposure/overview', response: V39_OVERVIEW },
            { match: '/api/v39/rogue-agents/cases', response: V39_CASES },
        ]);
        render(<V39AutonomousExposureValidationView />);
        await waitFor(() => {
            expect(screen.getByText('web-01')).toBeInTheDocument();
        });
        expect(screen.getByText(/2 critical · 1 KEV/)).toBeInTheDocument();
    });

    it('renders identity anomalies', async () => {
        installFetchMock([
            { match: '/api/v39/exposure/overview', response: V39_OVERVIEW },
            { match: '/api/v39/rogue-agents/cases', response: V39_CASES },
        ]);
        render(<V39AutonomousExposureValidationView />);
        await waitFor(() => {
            expect(screen.getByText('alice')).toBeInTheDocument();
        });
        expect(screen.getByText('82%')).toBeInTheDocument();
    });

    it('renders the Investigate button and empty agent form', async () => {
        installFetchMock([
            { match: '/api/v39/exposure/overview', response: V39_OVERVIEW },
            { match: '/api/v39/rogue-agents/cases', response: V39_CASES },
        ]);
        render(<V39AutonomousExposureValidationView />);
        expect(screen.getByRole('button', { name: /Investigate/i })).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/agent_id from runtime telemetry/i)).toBeInTheDocument();
    });

    it('stages an investigation with a root cause and containment plan', async () => {
        installFetchMock([
            { match: '/api/v39/exposure/overview', response: V39_OVERVIEW },
            { match: '/api/v39/rogue-agents/cases', response: V39_CASES },
            { match: '/api/v39/rogue-agents/investigate', response: V39_INVESTIGATION },
        ]);
        render(<V39AutonomousExposureValidationView />);
        fireEvent.change(screen.getByPlaceholderText(/agent_id from runtime telemetry/i), { target: { value: 'suspicious-agent-1' } });
        fireEvent.click(screen.getByRole('button', { name: /Investigate/i }));
        await waitFor(() => {
            expect(screen.getByText(/Case case-42/)).toBeInTheDocument();
        });
        expect(screen.getByText(/78%/)).toBeInTheDocument();
        expect(screen.getByText(/Unknown agent invoked an unapproved tool/i)).toBeInTheDocument();
        expect(screen.getByText(/revoke_credentials/i)).toBeInTheDocument();
    });

    it('renders the security boundary callout', async () => {
        installFetchMock([
            { match: '/api/v39/exposure/overview', response: V39_OVERVIEW },
            { match: '/api/v39/rogue-agents/cases', response: V39_CASES },
        ]);
        render(<V39AutonomousExposureValidationView />);
        expect(screen.getByText(/No autonomous offensive action/i)).toBeInTheDocument();
    });

    it('renders the rogue-agent determination list', async () => {
        installFetchMock([
            { match: '/api/v39/exposure/overview', response: V39_OVERVIEW },
            { match: '/api/v39/rogue-agents/cases', response: V39_CASES },
        ]);
        render(<V39AutonomousExposureValidationView />);
        expect(screen.getByText(/How VEYRA determines whether an agent is rogue/i)).toBeInTheDocument();
        expect(screen.getByText(/preserve evidence first/i)).toBeInTheDocument();
    });
});