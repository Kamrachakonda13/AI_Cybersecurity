/**
 * Component tests for v31.jsx (Sudo Arsenal + Adversary Trace).
 */
import React from 'react';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup, fireEvent } from '@testing-library/react';

import { V31SudoArsenalView, V31AdversaryTraceView } from '../v31.jsx';
import { installFetchMock, seedAuthToken } from './_helpers.jsx';


const ARSENAL_OVERVIEW = { tool_count: 587, privileged_count: 42, hack_back: 'disabled' };

const ARSENAL_TOOLS = [
    { id: 'nmap', name: 'Nmap', category: 'Network Discovery', purpose: 'Asset/service discovery', execution_profile: 'approved_worker', access_tier: 'admin', privileged_usage: false },
    { id: 'metasploit', name: 'Metasploit Framework', category: 'Exploit Validation', purpose: 'Scanner modules only', execution_profile: 'isolated_lab_only', access_tier: 'privileged_admin', privileged_usage: true },
    { id: 'wireshark', name: 'Wireshark', category: 'Network Defense', purpose: 'Packet analysis', execution_profile: 'analyst_workstation', access_tier: 'admin', privileged_usage: false },
];

const NMAP_DETAIL = {
    id: 'nmap', name: 'Nmap', purpose: 'Asset/service discovery',
    ui_usage: { step_1: 'Open Tool Runner.', step_2: 'Search for Nmap.', step_3: 'Confirm target and scope.' },
    terminal_usage: { first_check: 'nmap --help' },
    help: { safe_workflow: 'Use only on approved targets.', expected_evidence: ['target/scope', 'timestamp'] },
    help_boundary: 'Governed security operations.',
};

const TRACE_PLAN = {
    steps: ['preserve evidence', 'correlate telemetry', 'reconstruct timeline'],
    outputs: ['investigation summary', 'evidence bundle reference'],
};


describe('V31SudoArsenalView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header and eyebrow', async () => {
        installFetchMock([
            { match: '/api/v31/arsenal/overview', response: ARSENAL_OVERVIEW },
            { match: '/api/v31/arsenal/tools', response: ARSENAL_TOOLS },
        ]);
        render(<V31SudoArsenalView />);
        expect(screen.getByText('VEYRA V3.1 · PRIVILEGED SECURITY TOOL CONTROL PLANE')).toBeInTheDocument();
        expect(screen.getByText('Sudo Security Arsenal')).toBeInTheDocument();
    });

    it('renders KPI counters after data loads', async () => {
        installFetchMock([
            { match: '/api/v31/arsenal/overview', response: ARSENAL_OVERVIEW },
            { match: '/api/v31/arsenal/tools', response: ARSENAL_TOOLS },
        ]);
        render(<V31SudoArsenalView />);
        await waitFor(() => {
            expect(screen.getByText('CATALOG')).toBeInTheDocument();
        });
        expect(screen.getByText('587')).toBeInTheDocument();
        expect(screen.getByText('42')).toBeInTheDocument();
        expect(screen.getByText('DISABLED')).toBeInTheDocument();
    });

    it('renders the tool list', async () => {
        installFetchMock([
            { match: '/api/v31/arsenal/overview', response: ARSENAL_OVERVIEW },
            { match: '/api/v31/arsenal/tools', response: ARSENAL_TOOLS },
        ]);
        render(<V31SudoArsenalView />);
        await waitFor(() => {
            expect(screen.getByText('Nmap')).toBeInTheDocument();
        });
        expect(screen.getByText('Metasploit Framework')).toBeInTheDocument();
        expect(screen.getByText('Wireshark')).toBeInTheDocument();
    });

    it('filters tool list via the search input', async () => {
        installFetchMock([
            { match: '/api/v31/arsenal/overview', response: ARSENAL_OVERVIEW },
            { match: '/api/v31/arsenal/tools', response: ARSENAL_TOOLS },
        ]);
        render(<V31SudoArsenalView />);
        await waitFor(() => {
            expect(screen.getByText('Nmap')).toBeInTheDocument();
        });
        const search = screen.getByPlaceholderText(/Search tools, categories or purpose/i);
        fireEvent.change(search, { target: { value: 'metasploit' } });
        await waitFor(() => {
            expect(screen.queryByText('Nmap')).not.toBeInTheDocument();
        });
        expect(screen.getByText('Metasploit Framework')).toBeInTheDocument();
    });

    it('renders the sudo gate callout', async () => {
        installFetchMock([
            { match: '/api/v31/arsenal/overview', response: ARSENAL_OVERVIEW },
            { match: '/api/v31/arsenal/tools', response: ARSENAL_TOOLS },
        ]);
        render(<V31SudoArsenalView />);
        await waitFor(() => {
            expect(screen.getByText(/No unrestricted browser shell/i)).toBeInTheDocument();
        });
    });

    it('marks privileged tools with a privileged_admin badge', async () => {
        installFetchMock([
            { match: '/api/v31/arsenal/overview', response: ARSENAL_OVERVIEW },
            { match: '/api/v31/arsenal/tools', response: ARSENAL_TOOLS },
        ]);
        render(<V31SudoArsenalView />);
        await waitFor(() => {
            expect(screen.getAllByText('privileged_admin').length).toBeGreaterThan(0);
        });
    });

    it('opens tool detail panel on click and shows terminal usage', async () => {
        installFetchMock([
            { match: '/api/v31/arsenal/overview', response: ARSENAL_OVERVIEW },
            { match: '/api/v31/arsenal/tools/nmap', response: NMAP_DETAIL },
            { match: '/api/v31/arsenal/tools', response: ARSENAL_TOOLS },
        ]);
        render(<V31SudoArsenalView />);
        await waitFor(() => {
            expect(screen.getByText('Nmap')).toBeInTheDocument();
        });
        fireEvent.click(screen.getByText('Nmap'));
        await waitFor(() => {
            expect(screen.getByText('nmap --help')).toBeInTheDocument();
        });
    });
});


describe('V31AdversaryTraceView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header and purpose callout', () => {
        installFetchMock([], { body: TRACE_PLAN, status: 200 });
        render(<V31AdversaryTraceView />);
        expect(screen.getByText('Adversary Trace')).toBeInTheDocument();
        expect(screen.getByText(/VEYRA never hacks back/i)).toBeInTheDocument();
    });

    it('renders the trace plan form inputs', () => {
        installFetchMock([], { body: TRACE_PLAN, status: 200 });
        render(<V31AdversaryTraceView />);
        expect(screen.getByPlaceholderText(/Source IP/)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Destination/)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Observed timestamp/)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Indicators/)).toBeInTheDocument();
    });

    it('stages a trace plan on button click', async () => {
        installFetchMock([
            { match: '/api/v31/trace/plan', response: TRACE_PLAN },
        ]);
        render(<V31AdversaryTraceView />);
        fireEvent.change(screen.getByPlaceholderText(/Source IP/), { target: { value: '10.0.0.5' } });
        fireEvent.click(screen.getByRole('button', { name: /Stage defensive trace plan/i }));
        await waitFor(() => {
            expect(screen.getByText(/Trace plan staged/i)).toBeInTheDocument();
        });
    });

    it('renders investigation workflow steps and outputs after staging', async () => {
        installFetchMock([
            { match: '/api/v31/trace/plan', response: TRACE_PLAN },
        ]);
        render(<V31AdversaryTraceView />);
        fireEvent.click(screen.getByRole('button', { name: /Stage defensive trace plan/i }));
        await waitFor(() => {
            expect(screen.getByText('preserve evidence')).toBeInTheDocument();
        });
        expect(screen.getByText('correlate telemetry')).toBeInTheDocument();
        expect(screen.getByText(/investigation summary/)).toBeInTheDocument();
    });
});