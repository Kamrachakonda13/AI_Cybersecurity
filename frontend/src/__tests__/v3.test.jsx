/**
 * Component tests for v3.jsx views.
 *
 * Focus on V3GraphView and V3ReconstructionView (simple single-fetch).
 */
import React from 'react';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';

import { V3GraphView, V3ReconstructionView } from '../v3.jsx';
import { installFetchMock, seedAuthToken } from './_helpers.jsx';


const GRAPH = {
    nodes: [
        { id: 'n1', label: 'web-01', type: 'asset', risk: 42 },
        { id: 'n2', label: 'alice', type: 'identity', risk: 88 },
    ],
    edges: [
        { src: 'n2', dst: 'n1' },
    ],
    legend: ['asset', 'identity', 'cloud'],   // 3 items → distinct from 2
};

const RECONSTRUCTION = {
    events: [
        { stage: 'execution', actor: 'alice', target: 'web-01', time: '2026-09-22T10:00:00Z', source: 'endpoint', detail: 'suspicious powershell', risk: 85 },
    ],
    warning: 'Timeline ordering is evidence correlation, not proof of causality.',
};


describe('V3GraphView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => {
        cleanup();
        vi.unstubAllGlobals();
    });

    it('shows a loading indicator before data arrives', () => {
        installFetchMock([{ match: '/api/v3/fabric/graph', response: GRAPH }]);
        render(<V3GraphView />);
        expect(screen.getByText(/Loading graph/i)).toBeInTheDocument();
    });

    it('renders node, edge and legend counts', async () => {
        installFetchMock([{ match: '/api/v3/fabric/graph', response: GRAPH }]);
        render(<V3GraphView />);

        await waitFor(() => {
            expect(screen.getByText('NODES')).toBeInTheDocument();
        });
        expect(screen.getByText('2')).toBeInTheDocument();   // nodes
        expect(screen.getByText('1')).toBeInTheDocument();   // edges
        expect(screen.getByText('3')).toBeInTheDocument();   // legend (same as nodes)
    });

    it('renders individual node labels', async () => {
        installFetchMock([{ match: '/api/v3/fabric/graph', response: GRAPH }]);
        render(<V3GraphView />);

        await waitFor(() => {
            expect(screen.getByText('web-01')).toBeInTheDocument();
        });
        expect(screen.getByText('alice')).toBeInTheDocument();
    });

    it('renders the causality disclaimer', async () => {
        installFetchMock([{ match: '/api/v3/fabric/graph', response: GRAPH }]);
        render(<V3GraphView />);

        await waitFor(() => {
            expect(screen.getByText(/does not infer causality/i)).toBeInTheDocument();
        });
    });
});


describe('V3ReconstructionView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => {
        cleanup();
        vi.unstubAllGlobals();
    });

    it('shows a loading indicator initially', () => {
        installFetchMock([{ match: '/api/v3/fabric/reconstruction', response: RECONSTRUCTION }]);
        render(<V3ReconstructionView />);
        expect(screen.getByText(/Loading reconstruction/i)).toBeInTheDocument();
    });

    it('renders correlated event chain', async () => {
        installFetchMock([{ match: '/api/v3/fabric/reconstruction', response: RECONSTRUCTION }]);
        render(<V3ReconstructionView />);

        await waitFor(() => {
            expect(screen.getByText(/EXECUTION/)).toBeInTheDocument();
        });
        expect(screen.getByText(/alice → web-01/)).toBeInTheDocument();
    });

    it('renders the warning banner', async () => {
        installFetchMock([{ match: '/api/v3/fabric/reconstruction', response: RECONSTRUCTION }]);
        render(<V3ReconstructionView />);

        await waitFor(() => {
            expect(screen.getByText(RECONSTRUCTION.warning)).toBeInTheDocument();
        });
    });

    it('shows empty state when no events', async () => {
        installFetchMock([
            { match: '/api/v3/fabric/reconstruction', response: { events: [], warning: '' } },
        ]);
        render(<V3ReconstructionView />);

        await waitFor(() => {
            expect(screen.getByText(/No correlated events yet/i)).toBeInTheDocument();
        });
    });
});