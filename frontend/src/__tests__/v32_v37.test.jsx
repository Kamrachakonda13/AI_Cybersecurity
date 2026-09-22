/**
 * Component tests for v32-v37 view components.
 *
 * Covers:
 *   - V32TeamAcademyView
 *   - V33SecurityReadinessView
 *   - V34SecurityIntelligenceView
 *   - V35SecurityLifecycleView
 *   - V36SecurityRadarView
 *   - V37SecurityGraphIntelligenceView
 */
import React from 'react';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';

import { V32TeamAcademyView } from '../v32.jsx';
import { V33SecurityReadinessView } from '../v33.jsx';
import { V34SecurityIntelligenceView } from '../v34.jsx';
import { V35SecurityLifecycleView } from '../v35.jsx';
import { V36SecurityRadarView } from '../v36.jsx';
import { V37SecurityGraphIntelligenceView } from '../v37.jsx';
import { installFetchMock, seedAuthToken } from './_helpers.jsx';


// ========== fixtures ==========

const V32_OVERVIEW = {
    levels: [
        { id: 'l1', name: 'Foundation', goal: 'Understand governed execution' },
        { id: 'l2', name: 'Operator', goal: 'Run scoped assessments' },
        { id: 'l3', name: 'Expert', goal: 'Design governed workflows' },
    ],
    tracks: [
        { id: 'ai-security', name: 'AI Security' },
        { id: 'soc-defender', name: 'SOC / Blue Team' },
    ],
    documentation_contract: ['purpose', 'ui_workflow', 'terminal', 'evidence'],
};

const V32_CURRICULUM = {
    track: 'AI Security',
    tools: [
        { id: 'pyrit', name: 'PyRIT', category: 'LLM Red Team', purpose: 'Adversarial testing', execution_profile: 'approved_ai_worker', access_tier: 'admin' },
    ],
};

const V33_OVERVIEW = {
    documentation: {
        documented_tools: 587,
        registered_tools: 587,
        coverage_percent: 100,
        missing_tools: [],
    },
    domains: [
        { id: 'identity', name: 'Identity & Privilege', description: 'Least privilege' },
        { id: 'scope', name: 'Scope & Authorization', description: 'Explicit target scope' },
    ],
    exercise_count: 6,
};

const V33_EXERCISES = {
    exercises: [
        { id: 'ai-agent-abuse', name: 'AI Agent Abuse Drill', goal: 'Detect unauthorized tool action', evidence: ['agent trace', 'policy decision'] },
    ],
};

const V34_OVERVIEW = {
    inventory: { assets: 10, ai_assets: 3 },
    signals: [
        { id: 'sig-1', message: 'AI asset without provenance', priority: 'high' },
        { id: 'sig-2', message: 'Pending approval queue', priority: 'low' },
    ],
    control_tests: [{ id: 't1' }, { id: 't2' }],
};

const V34_PLAN = {
    tests: [
        { id: 'test-1', name: 'Verify identity controls', frequency: 'weekly', evidence: ['auth events', 'policy decisions'] },
    ],
};

const V35_OVERVIEW = {
    stages: [
        { id: 's1', name: 'Discover', description: 'Inventory assets', evidence: ['asset list'], status: 'complete' },
        { id: 's2', name: 'Validate', description: 'Run controls', evidence: ['control receipt'], status: 'attention' },
        { id: 's3', name: 'Contain', description: 'Approve containment', evidence: ['containment plan'], status: 'pending' },
    ],
    inventory: { evidence: 25 },
};

const V35_PLAN = {
    stages: [
        { id: 'p1', name: 'Plan stage 1', description: 'Detailed planning' },
        { id: 'p2', name: 'Plan stage 2', description: 'Second stage' },
    ],
};

const V36_DATA = {
    recommendations: [
        { id: 'r1', name: 'Kyverno 1.18+', kind: 'tool', maturity: 'recommended', source: 'CNCF', reason: 'Policy-as-code', maps_to: ['Kubernetes governance'] },
        { id: 'r2', name: 'Prempti', kind: 'tool', maturity: 'experimental', source: 'Falco', reason: 'Runtime visibility', maps_to: ['agent runtime'] },
        { id: 'r3', name: 'OWASP ACS', kind: 'standard', maturity: 'recommended', source: 'OWASP', reason: 'Agent control standard', maps_to: ['governance'] },
    ],
};

const V37_INTEL = {
    inventory: { assets: 10, ai_assets: 3 },
    controls: [
        { id: 'c1', name: 'Identity controls', references: ['NIST AC-2'], status: 'covered' },
        { id: 'c2', name: 'AI runtime controls', references: ['NIST AI RMF'], status: 'attention' },
    ],
    graph: { nodes: 42, edges: 88 },
    attack_paths: [
        { target_label: 'payment-api', length: 3, risk: 78, steps: [{ from: 'alice', to: 'agent-1' }] },
    ],
    hotspots: [
        { node: 'n1', label: 'soc-agent', kind: 'agent', connections: 12, risk_score: 85 },
    ],
    chokepoints: [
        { node: 'c1', label: 'API gateway', paths: 4 },
    ],
    drift_signals: [
        { reason: 'Evidence for 2 controls is older than retention policy.' },
    ],
};

const V37_EVIDENCE = {
    evidence_receipts: [
        { artifact_id: 'art-1', source: 'worker-1', result_type: 'scan', classification: 'internal', job_id: 'job-7', sha256: 'deadbeef' },
    ],
};


// ========== V32TeamAcademyView ==========

describe('V32TeamAcademyView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header', async () => {
        installFetchMock([
            { match: '/api/v32/academy/overview', response: V32_OVERVIEW },
            { match: '/api/v32/academy/curriculum', response: V32_CURRICULUM },
        ]);
        render(<V32TeamAcademyView />);
        expect(screen.getByText('VEYRA V3.2 · TEAM ENABLEMENT')).toBeInTheDocument();
        expect(screen.getByText('Security Team Academy')).toBeInTheDocument();
    });

    it('renders learning levels after data loads', async () => {
        installFetchMock([
            { match: '/api/v32/academy/overview', response: V32_OVERVIEW },
            { match: '/api/v32/academy/curriculum', response: V32_CURRICULUM },
        ]);
        render(<V32TeamAcademyView />);
        await waitFor(() => {
            expect(screen.getByText('FOUNDATION')).toBeInTheDocument();
        });
        expect(screen.getByText('OPERATOR')).toBeInTheDocument();
        expect(screen.getByText('EXPERT')).toBeInTheDocument();
    });

    it('renders curriculum tools', async () => {
        installFetchMock([
            { match: '/api/v32/academy/overview', response: V32_OVERVIEW },
            { match: '/api/v32/academy/curriculum', response: V32_CURRICULUM },
        ]);
        render(<V32TeamAcademyView />);
        await waitFor(() => {
            expect(screen.getByText('PyRIT')).toBeInTheDocument();
        });
        expect(screen.getByText('LLM Red Team · Adversarial testing')).toBeInTheDocument();
    });

    it('renders documentation contract items', async () => {
        installFetchMock([
            { match: '/api/v32/academy/overview', response: V32_OVERVIEW },
            { match: '/api/v32/academy/curriculum', response: V32_CURRICULUM },
        ]);
        render(<V32TeamAcademyView />);
        await waitFor(() => {
            expect(screen.getByText('purpose')).toBeInTheDocument();
        });
        expect(screen.getByText('ui workflow')).toBeInTheDocument();
    });
});


// ========== V33SecurityReadinessView ==========

describe('V33SecurityReadinessView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header', async () => {
        installFetchMock([
            { match: '/api/v33/readiness/overview', response: V33_OVERVIEW },
            { match: '/api/v33/readiness/exercises', response: V33_EXERCISES },
        ]);
        render(<V33SecurityReadinessView />);
        expect(screen.getByText('Security Readiness Center')).toBeInTheDocument();
    });

    it('renders documentation coverage KPI', async () => {
        installFetchMock([
            { match: '/api/v33/readiness/overview', response: V33_OVERVIEW },
            { match: '/api/v33/readiness/exercises', response: V33_EXERCISES },
        ]);
        render(<V33SecurityReadinessView />);
        await waitFor(() => {
            expect(screen.getByText('587/587')).toBeInTheDocument();
        });
        expect(screen.getByText('100% documented')).toBeInTheDocument();
    });

    it('renders control domains', async () => {
        installFetchMock([
            { match: '/api/v33/readiness/overview', response: V33_OVERVIEW },
            { match: '/api/v33/readiness/exercises', response: V33_EXERCISES },
        ]);
        render(<V33SecurityReadinessView />);
        await waitFor(() => {
            expect(screen.getByText('Identity & Privilege')).toBeInTheDocument();
        });
        expect(screen.getByText('Scope & Authorization')).toBeInTheDocument();
    });

    it('renders exercise library', async () => {
        installFetchMock([
            { match: '/api/v33/readiness/overview', response: V33_OVERVIEW },
            { match: '/api/v33/readiness/exercises', response: V33_EXERCISES },
        ]);
        render(<V33SecurityReadinessView />);
        await waitFor(() => {
            expect(screen.getByText('AI Agent Abuse Drill')).toBeInTheDocument();
        });
    });

    it('shows all-documented message when nothing missing', async () => {
        installFetchMock([
            { match: '/api/v33/readiness/overview', response: V33_OVERVIEW },
            { match: '/api/v33/readiness/exercises', response: V33_EXERCISES },
        ]);
        render(<V33SecurityReadinessView />);
        await waitFor(() => {
            expect(screen.getByText(/all registered tools have an individual Markdown help page/i)).toBeInTheDocument();
        });
    });
});


// ========== V34SecurityIntelligenceView ==========

describe('V34SecurityIntelligenceView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header', async () => {
        installFetchMock([
            { match: '/api/v34/intelligence/overview', response: V34_OVERVIEW },
            { match: '/api/v34/validation/plan', response: V34_PLAN },
        ]);
        render(<V34SecurityIntelligenceView />);
        expect(screen.getByText('Continuous Security Validation')).toBeInTheDocument();
    });

    it('renders KPI tiles', async () => {
        installFetchMock([
            { match: '/api/v34/intelligence/overview', response: V34_OVERVIEW },
            { match: '/api/v34/validation/plan', response: V34_PLAN },
        ]);
        render(<V34SecurityIntelligenceView />);
        await waitFor(() => {
            expect(screen.getByText('ASSETS')).toBeInTheDocument();
        });
        expect(screen.getByText('AI ASSETS')).toBeInTheDocument();
        expect(screen.getByText('CONTROL TESTS')).toBeInTheDocument();
    });

    it('renders priority signals with severity badges', async () => {
        installFetchMock([
            { match: '/api/v34/intelligence/overview', response: V34_OVERVIEW },
            { match: '/api/v34/validation/plan', response: V34_PLAN },
        ]);
        render(<V34SecurityIntelligenceView />);
        await waitFor(() => {
            expect(screen.getByText('sig-1')).toBeInTheDocument();
        });
        expect(screen.getByText('HIGH')).toBeInTheDocument();
        expect(screen.getByText('LOW')).toBeInTheDocument();
    });

    it('renders validation plan tests', async () => {
        installFetchMock([
            { match: '/api/v34/intelligence/overview', response: V34_OVERVIEW },
            { match: '/api/v34/validation/plan', response: V34_PLAN },
        ]);
        render(<V34SecurityIntelligenceView />);
        await waitFor(() => {
            expect(screen.getByText('Verify identity controls')).toBeInTheDocument();
        });
    });
});


// ========== V35SecurityLifecycleView ==========

describe('V35SecurityLifecycleView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header', async () => {
        installFetchMock([
            { match: '/api/v35/lifecycle/overview', response: V35_OVERVIEW },
            { match: '/api/v35/lifecycle/plan', response: V35_PLAN },
        ]);
        render(<V35SecurityLifecycleView />);
        expect(screen.getByText('Security Operations Lifecycle')).toBeInTheDocument();
    });

    it('renders lifecycle stages with numbered labels and status', async () => {
        installFetchMock([
            { match: '/api/v35/lifecycle/overview', response: V35_OVERVIEW },
            { match: '/api/v35/lifecycle/plan', response: V35_PLAN },
        ]);
        render(<V35SecurityLifecycleView />);
        await waitFor(() => {
            expect(screen.getByText(/1\. Discover/)).toBeInTheDocument();
        });
        expect(screen.getByText(/3\. Contain/)).toBeInTheDocument();
    });

    it('renders attention count KPI', async () => {
        installFetchMock([
            { match: '/api/v35/lifecycle/overview', response: V35_OVERVIEW },
            { match: '/api/v35/lifecycle/plan', response: V35_PLAN },
        ]);
        render(<V35SecurityLifecycleView />);
        await waitFor(() => {
            expect(screen.getByText('ATTENTION')).toBeInTheDocument();
        });
    });

    it('renders the governance boundary callout', async () => {
        installFetchMock([
            { match: '/api/v35/lifecycle/overview', response: V35_OVERVIEW },
            { match: '/api/v35/lifecycle/plan', response: V35_PLAN },
        ]);
        render(<V35SecurityLifecycleView />);
        await waitFor(() => {
            expect(screen.getByText(/hack-back is disabled/i)).toBeInTheDocument();
        });
    });
});


// ========== V36SecurityRadarView ==========

describe('V36SecurityRadarView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header', async () => {
        installFetchMock([{ match: '/api/v36/security-radar', response: V36_DATA }]);
        render(<V36SecurityRadarView />);
        expect(screen.getByText('Security Tool & Control Radar')).toBeInTheDocument();
    });

    it('renders KPI totals', async () => {
        installFetchMock([{ match: '/api/v36/security-radar', response: V36_DATA }]);
        render(<V36SecurityRadarView />);
        await waitFor(() => {
            expect(screen.getByText('RADAR ITEMS')).toBeInTheDocument();
        });
        // 3 total items
        expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('renders recommendation rows', async () => {
        installFetchMock([{ match: '/api/v36/security-radar', response: V36_DATA }]);
        render(<V36SecurityRadarView />);
        await waitFor(() => {
            expect(screen.getByText('Kyverno 1.18+')).toBeInTheDocument();
        });
        expect(screen.getByText('Prempti')).toBeInTheDocument();
    });

    it('renders maturity badges', async () => {
        installFetchMock([{ match: '/api/v36/security-radar', response: V36_DATA }]);
        render(<V36SecurityRadarView />);
        await waitFor(() => {
            expect(screen.getAllByText('RECOMMENDED').length).toBeGreaterThan(0);
        });
        expect(screen.getAllByText('EXPERIMENTAL').length).toBeGreaterThan(0);
    });
});


// ========== V37SecurityGraphIntelligenceView ==========

describe('V37SecurityGraphIntelligenceView', () => {
    beforeEach(() => seedAuthToken());
    afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

    it('renders the header', async () => {
        installFetchMock([
            { match: '/api/v37/security-graph/intelligence', response: V37_INTEL },
            { match: '/api/v37/security-graph/control-evidence', response: V37_EVIDENCE },
        ]);
        render(<V37SecurityGraphIntelligenceView />);
        expect(screen.getByText('Unified Security Graph Intelligence')).toBeInTheDocument();
    });

    it('renders graph KPI counts', async () => {
        installFetchMock([
            { match: '/api/v37/security-graph/intelligence', response: V37_INTEL },
            { match: '/api/v37/security-graph/control-evidence', response: V37_EVIDENCE },
        ]);
        render(<V37SecurityGraphIntelligenceView />);
        await waitFor(() => {
            expect(screen.getByText('42')).toBeInTheDocument();
        });
        expect(screen.getByText('88')).toBeInTheDocument();
    });

    it('renders graph hotspots', async () => {
        installFetchMock([
            { match: '/api/v37/security-graph/intelligence', response: V37_INTEL },
            { match: '/api/v37/security-graph/control-evidence', response: V37_EVIDENCE },
        ]);
        render(<V37SecurityGraphIntelligenceView />);
        await waitFor(() => {
            expect(screen.getByText('soc-agent')).toBeInTheDocument();
        });
        expect(screen.getByText('risk 85')).toBeInTheDocument();
    });

    it('renders drift signals callout', async () => {
        installFetchMock([
            { match: '/api/v37/security-graph/intelligence', response: V37_INTEL },
            { match: '/api/v37/security-graph/control-evidence', response: V37_EVIDENCE },
        ]);
        render(<V37SecurityGraphIntelligenceView />);
        await waitFor(() => {
            expect(screen.getByText(/older than retention policy/i)).toBeInTheDocument();
        });
    });

    it('renders attack paths panel', async () => {
        installFetchMock([
            { match: '/api/v37/security-graph/intelligence', response: V37_INTEL },
            { match: '/api/v37/security-graph/control-evidence', response: V37_EVIDENCE },
        ]);
        render(<V37SecurityGraphIntelligenceView />);
        await waitFor(() => {
            expect(screen.getByText('payment-api')).toBeInTheDocument();
        });
        expect(screen.getByText('PATH')).toBeInTheDocument();
    });
});