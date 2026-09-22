import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { V60ChecklistsView } from '../v60_checklists.jsx';
import { V61LiveOpsView } from '../v61_live_ops.jsx';
import { V62TeamDashView } from '../v62_team_dash.jsx';
import { V63TrendsView } from '../v63_trends.jsx';
import { V64DomainToolsView } from '../v64_domain_tools.jsx';
import { V65AgentClassificationView } from '../v65_agent_classification.jsx';

beforeEach(() => {
  global.fetch = vi.fn((url) => {
    if (String(url).includes('/api/v60/checklists')) return Promise.resolve({ json: () => Promise.resolve({ checklists: [{ id: 'mfa-coverage', name: 'MFA coverage', domain: 'identity', category: 'Auth', purpose: 'test', owner_role: 'security_admin', cadence: 'daily', tier: 'essential', evidence: ['a'], boundary: 'b' }] }) });
    if (String(url).includes('/api/v60/runs')) return Promise.resolve({ json: () => Promise.resolve([]) });
    if (String(url).includes('/api/v61/events')) return Promise.resolve({ json: () => Promise.resolve([]) });
    if (String(url).includes('/api/v61/drops')) return Promise.resolve({ json: () => Promise.resolve([]) });
    if (String(url).includes('/api/v61/baselines')) return Promise.resolve({ json: () => Promise.resolve([]) });
    if (String(url).includes('/api/v60/trends')) return Promise.resolve({ json: () => Promise.resolve({ coverage: { percent: 10, exercised: 2, total_definitions: 74 }, posture_series: [], mttr: [], regressions: [] }) });
    if (String(url).includes('/api/domains/overview')) return Promise.resolve({ json: () => Promise.resolve({ domains: [{ domain: 'Network Security', count: 50, categories: { 'Network Discovery': 5 }, vendors: ['Cisco'] }] }) });
    if (String(url).includes('/api/agents/classification')) return Promise.resolve({ json: () => Promise.resolve({ total_agents: 0, by_class: {}, agents: [], note: '' }) });
    return Promise.resolve({ json: () => Promise.resolve([]) });
  });
});

describe('P6 views', () => {
  it('V60ChecklistsView renders', async () => {
    const { container } = render(<V60ChecklistsView />);
    expect(container.textContent).toContain('Checklist Library');
  });
  it('V61LiveOpsView renders', async () => {
    const { container } = render(<V61LiveOpsView />);
    expect(container.textContent).toContain('Live Operations');
  });
  it('V62TeamDashView renders', async () => {
    const { container } = render(<V62TeamDashView />);
    expect(container.textContent).toContain('Team Dashboards');
  });
  it('V63TrendsView renders', async () => {
    const { container } = render(<V63TrendsView />);
    expect(container.textContent).toContain('Trends');
  });
  it('V64DomainToolsView renders', async () => {
    const { container } = render(<V64DomainToolsView />);
    expect(container.textContent).toContain('Security Domains');
  });
  it('V65AgentClassificationView renders', async () => {
    const { container } = render(<V65AgentClassificationView />);
    expect(container.textContent).toContain('Agent Classification');
  });
});
