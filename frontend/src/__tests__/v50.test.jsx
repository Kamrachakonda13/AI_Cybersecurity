/**
 * Component tests for v50.jsx (control plane) and v50_ai_apps.jsx (AI apps).
 */
import React from 'react';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup, fireEvent } from '@testing-library/react';

import { V50AutonomousSecurityControlPlane } from '../v50.jsx';
import { V50AIApplicationsView } from '../v50_ai_apps.jsx';
import { installFetchMock, seedAuthToken } from './_helpers.jsx';


// ---------- v50.jsx fixtures ----------

const V50_OVERVIEW = {
    trust_invariant: 'No asset becomes trusted merely because it exists.',
    gates: [
        'identity', 'provenance', 'integrity', 'policy_compliance',
        'validation', 'deployment_control', 'runtime_attestation',
        'behavioral_baseline', 'trajectory_assurance',
        'evidence_integrity', 'circuit_breaker_readiness',
    ],
    graph_nodes: 42,
};

const V50_ASSETS = [
    {
        asset_id: 'agent-1', name: 'SOC Agent', asset_type: 'agent',
        version: '1.0.0', digest: 'sha256:abc', trust_status: 'trusted',
    },
    {
        asset_id: 'model-1', name: 'Unverified Model', asset_type: 'model',
        version: '0.5.0', digest: '', trust_status: 'untrusted',
    },
];

const V50_DECISIONS = [
    { decision_id: 'd-1', subject_id: 'agent-1', decision: 'allow', reason: 'all gates passed', evidence_sha256: 'deadbeef'.repeat(8) },
    { decision_id: 'd-2', subject_id: 'model-1', decision: 'deny', reason: 'missing provenance', evidence_sha256: 'cafebabe'.repeat(8) },
];


// ---------- v50_ai_apps.jsx fixtures ----------

const AI_CATALOG = {
    applications: [
        { id: 'cybsoc_rag', name: 'CyberSOC RAG — AI Security Analyst', category: 'RAG + Cybersecurity', description: 'Hybrid evidence retrieval' },
        { id: 'vulnerability_intelligence_rag', name: 'Vulnerability Intelligence RAG', category: 'RAG + Cybersecurity', description: 'CVE/KEV prioritization' },
        { id: 'autonomous_research_agent', name: 'Autonomous Research Agent', category: 'Agentic AI', description: 'Planner workflow' },
        { id: 'agentic_incident_response', name: 'Agentic Cybersecurity Incident Response', category: 'Agentic AI', description: 'Evidence-driven investigation' },
        { id: 'enterprise_ai_decision_platform', name: 'Enterprise AI Knowledge & Decision Platform', category: 'AI / GenAI', description: 'Governed router' },
        { id: 'llm_evaluation_reliability', name: 'LLM Evaluation & AI Reliability Platform', category: 'AI / GenAI', description: 'RAG/agent/model evaluation' },
    ],
};


// ---------- tests ----------

describe('V50AutonomousSecurityControlPlane', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => {
        cleanup();
        vi.unstubAllGlobals();
    });

    it('renders the header and title', async () => {
        installFetchMock([
            { match: '/api/v50/overview', response: V50_OVERVIEW },
            { match: '/api/v50/ai-assets', response: [] },
            { match: '/api/v50/decisions', response: [] },
        ]);
        render(<V50AutonomousSecurityControlPlane />);
        expect(screen.getByText('VEYRA v5.0 · AUTONOMOUS SECURITY CONTROL PLANE')).toBeInTheDocument();
        expect(screen.getByText('Continuous trust, not implicit trust')).toBeInTheDocument();
    });

    it('renders the trust invariant after data loads', async () => {
        installFetchMock([
            { match: '/api/v50/overview', response: V50_OVERVIEW },
            { match: '/api/v50/ai-assets', response: [] },
            { match: '/api/v50/decisions', response: [] },
        ]);
        render(<V50AutonomousSecurityControlPlane />);
        await waitFor(() => {
            expect(screen.getByText(V50_OVERVIEW.trust_invariant)).toBeInTheDocument();
        });
    });

    it('renders trust gates (falls back to built-in list when overview is empty)', async () => {
        installFetchMock([
            { match: '/api/v50/overview', response: {} },
            { match: '/api/v50/ai-assets', response: [] },
            { match: '/api/v50/decisions', response: [] },
        ]);
        render(<V50AutonomousSecurityControlPlane />);
        // Falls back to inline gates array; "1. identity" renders inside a <b>.
        // Query by substring since React splits the number/dot/name into nodes.
        await waitFor(() => {
            const gates = screen.getAllByText((_content, element) =>
                element?.tagName === 'B' && /identity/.test(element.textContent)
            );
            expect(gates.length).toBeGreaterThan(0);
        });
    });

    it('renders AI supply-chain assets', async () => {
        installFetchMock([
            { match: '/api/v50/overview', response: V50_OVERVIEW },
            { match: '/api/v50/ai-assets', response: V50_ASSETS },
            { match: '/api/v50/decisions', response: [] },
        ]);
        render(<V50AutonomousSecurityControlPlane />);
        await waitFor(() => {
            expect(screen.getByText('SOC Agent')).toBeInTheDocument();
        });
        expect(screen.getByText('Unverified Model')).toBeInTheDocument();
    });

    it('renders trust decisions with allow/deny badges', async () => {
        installFetchMock([
            { match: '/api/v50/overview', response: V50_OVERVIEW },
            { match: '/api/v50/ai-assets', response: [] },
            { match: '/api/v50/decisions', response: V50_DECISIONS },
        ]);
        render(<V50AutonomousSecurityControlPlane />);
        await waitFor(() => {
            expect(screen.getByText('agent-1')).toBeInTheDocument();
        });
        expect(screen.getByText('allow')).toBeInTheDocument();
        expect(screen.getByText('deny')).toBeInTheDocument();
    });

    it('shows empty-state for no registered assets', async () => {
        installFetchMock([
            { match: '/api/v50/overview', response: V50_OVERVIEW },
            { match: '/api/v50/ai-assets', response: [] },
            { match: '/api/v50/decisions', response: [] },
        ]);
        render(<V50AutonomousSecurityControlPlane />);
        await waitFor(() => {
            expect(screen.getByText(/No v5 AI supply-chain assets registered/i)).toBeInTheDocument();
        });
    });

    it('shows empty-state for no trust decisions', async () => {
        installFetchMock([
            { match: '/api/v50/overview', response: V50_OVERVIEW },
            { match: '/api/v50/ai-assets', response: [] },
            { match: '/api/v50/decisions', response: [] },
        ]);
        render(<V50AutonomousSecurityControlPlane />);
        await waitFor(() => {
            expect(screen.getByText(/No trust decisions recorded/i)).toBeInTheDocument();
        });
    });

    it('renders control modes panel', async () => {
        installFetchMock([
            { match: '/api/v50/overview', response: V50_OVERVIEW },
            { match: '/api/v50/ai-assets', response: [] },
            { match: '/api/v50/decisions', response: [] },
        ]);
        render(<V50AutonomousSecurityControlPlane />);
        await waitFor(() => {
            expect(screen.getByText('OBSERVE')).toBeInTheDocument();
        });
        expect(screen.getByText('APPROVAL REQUIRED')).toBeInTheDocument();
        expect(screen.getByText('ENFORCE')).toBeInTheDocument();
        expect(screen.getByText('EMERGENCY STOP')).toBeInTheDocument();
    });

    it('renders the Register + evaluate trust button', async () => {
        installFetchMock([
            { match: '/api/v50/overview', response: V50_OVERVIEW },
            { match: '/api/v50/ai-assets', response: [] },
            { match: '/api/v50/decisions', response: [] },
        ]);
        render(<V50AutonomousSecurityControlPlane />);
        expect(screen.getByRole('button', { name: /Register \+ evaluate trust/i })).toBeInTheDocument();
    });

    it('renders static info panels (Trajectory assurance, MCP Rug-Pull, etc.)', async () => {
        installFetchMock([
            { match: '/api/v50/overview', response: V50_OVERVIEW },
            { match: '/api/v50/ai-assets', response: [] },
            { match: '/api/v50/decisions', response: [] },
        ]);
        render(<V50AutonomousSecurityControlPlane />);
        expect(screen.getByText('Trajectory assurance')).toBeInTheDocument();
        expect(screen.getByText('MCP Rug-Pull Detection')).toBeInTheDocument();
        expect(screen.getByText('Agent Memory Security')).toBeInTheDocument();
        expect(screen.getByText('Agent Behavioral DNA')).toBeInTheDocument();
        expect(screen.getByText('AI Security Digital Twin')).toBeInTheDocument();
    });
});


describe('V50AIApplicationsView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => {
        cleanup();
        vi.unstubAllGlobals();
    });

    it('renders the header', async () => {
        installFetchMock([
            { match: '/api/v50/ai-applications/catalog', response: AI_CATALOG },
        ]);
        render(<V50AIApplicationsView />);
        expect(screen.getByText('VEYRA v5.0 · AI APPLICATIONS')).toBeInTheDocument();
        expect(screen.getByText('Six portfolio-grade AI security applications')).toBeInTheDocument();
    });

    it('renders application buttons from the catalog', async () => {
        installFetchMock([
            { match: '/api/v50/ai-applications/catalog', response: AI_CATALOG },
        ]);
        render(<V50AIApplicationsView />);
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /CyberSOC RAG/ })).toBeInTheDocument();
        });
        expect(screen.getByRole('button', { name: /Vulnerability Intelligence RAG/ })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Autonomous Research Agent/ })).toBeInTheDocument();
    });

    it('shows the empty result state initially', async () => {
        installFetchMock([
            { match: '/api/v50/ai-applications/catalog', response: AI_CATALOG },
        ]);
        render(<V50AIApplicationsView />);
        await waitFor(() => {
            expect(screen.getByText(/Run the selected application/i)).toBeInTheDocument();
        });
    });

    it('renders the query input and Run POC button', async () => {
        installFetchMock([
            { match: '/api/v50/ai-applications/catalog', response: AI_CATALOG },
        ]);
        render(<V50AIApplicationsView />);
        expect(screen.getByRole('button', { name: /Run POC/i })).toBeInTheDocument();
        const input = screen.getByPlaceholderText(/Question \/ investigation task/i);
        expect(input).toBeInTheDocument();
        expect(input.value).toMatch(/Investigate failed logins/i);
    });

    it('runs the default cybsoc_rag POC and renders the answer', async () => {
        installFetchMock([
            { match: '/api/v50/ai-applications/catalog', response: AI_CATALOG },
            {
                match: '/api/v50/ai-applications/cybsoc-rag',
                response: {
                    application: 'cybsoc_rag',
                    answer: 'Investigation focuses on the query. Evidence links identity and endpoint telemetry.',
                    retrieval: [{ id: 'r1', title: 'Suspicious PowerShell', citation: '[soc-001]' }],
                    citations: ['[soc-001]'],
                    grounded: true,
                },
            },
        ]);
        render(<V50AIApplicationsView />);
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Run POC/i })).toBeInTheDocument();
        });
        fireEvent.click(screen.getByRole('button', { name: /Run POC/i }));

        await waitFor(() => {
            expect(screen.getByText(/Investigation focuses on the query/i)).toBeInTheDocument();
        });
        expect(screen.getByText('[soc-001]')).toBeInTheDocument();
    });

    it('runs the vulnerability_intelligence_rag POC and renders the priority queue', async () => {
        installFetchMock([
            { match: '/api/v50/ai-applications/catalog', response: AI_CATALOG },
            {
                match: '/api/v50/ai-applications/vulnerability-rag',
                response: {
                    application: 'vulnerability_intelligence_rag',
                    priority_queue: [
                        { asset: 'payment-api', cve: 'CVE-2025-0001', risk_score: 96.6, reason: 'CISA KEV; internet-facing' },
                    ],
                },
            },
        ]);
        render(<V50AIApplicationsView />);
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Vulnerability Intelligence RAG/ })).toBeInTheDocument();
        });
        fireEvent.click(screen.getByRole('button', { name: /Vulnerability Intelligence RAG/ }));
        fireEvent.click(screen.getByRole('button', { name: /Run POC/i }));

        await waitFor(() => {
            expect(screen.getByText(/payment-api · CVE-2025-0001/)).toBeInTheDocument();
        });
        expect(screen.getByText(/Risk 96\.6/)).toBeInTheDocument();
    });
});