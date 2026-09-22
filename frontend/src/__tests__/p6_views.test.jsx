import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { V60ChecklistsView } from '../v60_checklists.jsx';
import { V61LiveOpsView } from '../v61_live_ops.jsx';
import { V62TeamDashView } from '../v62_team_dash.jsx';
import { V63TrendsView } from '../v63_trends.jsx';

beforeEach(() => {
  global.fetch = vi.fn((url) => {
    if (String(url).includes('/api/v60/checklists')) return Promise.resolve({ json: () => Promise.resolve({ checklists: [{ id: 'mfa-coverage', name: 'MFA coverage', domain: 'identity', category: 'Auth', purpose: 'test', owner_role: 'security_admin', cadence: 'daily', tier: 'essential', evidence: ['a'], boundary: 'b' }] }) });
    if (String(url).includes('/api/v60/runs')) return Promise.resolve({ json: () => Promise.resolve([]) });
    if (String(url).includes('/api/v61/events')) return Promise.resolve({ json: () => Promise.resolve([]) });
    if (String(url).includes('/api/v61/drops')) return Promise.resolve({ json: () => Promise.resolve([]) });
    if (String(url).includes('/api/v61/baselines')) return Promise.resolve({ json: () => Promise.resolve([]) });
    if (String(url).includes('/api/v60/trends')) return Promise.resolve({ json: () => Promise.resolve({ coverage: { percent: 10, exercised: 2, total_definitions: 74 }, posture_series: [], mttr: [], regressions: [] }) });
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
});
