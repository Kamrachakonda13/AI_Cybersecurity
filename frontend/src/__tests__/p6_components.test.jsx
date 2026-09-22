import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { StatusChip } from '../components/StatusChip.jsx';
import { StatusPie } from '../components/StatusPie.jsx';
import { Sparkline } from '../components/Sparkline.jsx';
import { Sparkbar } from '../components/Sparkbar.jsx';
import { HeatGrid } from '../components/HeatGrid.jsx';
import { DropTimeline } from '../components/DropTimeline.jsx';
import { TrendCard } from '../components/TrendCard.jsx';
import { NAV } from '../lib/nav.js';

describe('P6 components', () => {
  it('StatusChip renders all chips', () => {
    for (const chip of ['green', 'amber', 'yellow', 'semi_red', 'red']) {
      const { container } = render(<StatusChip chip={chip} />);
      expect(container.querySelector('[data-testid="status-chip"]')).toBeTruthy();
    }
  });
  it('StatusPie renders', () => {
    const { container } = render(<StatusPie segments={[{ chip: 'green', value: 3 }, { chip: 'red', value: 1 }]} />);
    expect(container.querySelector('[data-testid="status-pie"]')).toBeTruthy();
  });
  it('Sparkline renders', () => {
    const { container } = render(<Sparkline data={[1, 3, 2, 5]} />);
    expect(container.querySelector('[data-testid="sparkline"]')).toBeTruthy();
  });
  it('Sparkbar renders', () => {
    const { container } = render(<Sparkbar data={[2, 4, 1]} />);
    expect(container.querySelector('[data-testid="sparkbar"]')).toBeTruthy();
  });
  it('HeatGrid renders', () => {
    const { container } = render(<HeatGrid cells={Array(14).fill('green')} />);
    expect(container.querySelector('[data-testid="heatgrid"]')).toBeTruthy();
  });
  it('DropTimeline renders', () => {
    const { container } = render(<DropTimeline drops={[{ drop_id: 'd1', link_id: 'eth0', link_type: 'ethernet', created_at: new Date().toISOString() }]} />);
    expect(container.querySelector('[data-testid="drop-timeline"]')).toBeTruthy();
  });
  it('TrendCard renders', () => {
    const { container } = render(<TrendCard title="Test" value="5" chip="green" data={[1, 2, 3]} />);
    expect(container.querySelector('[data-testid="trend-card"]')).toBeTruthy();
  });
  it('NAV has checklist + live ops entries', () => {
    const names = NAV.map((n) => n[0]);
    expect(names).toContain('Checklist Library');
    expect(names).toContain('Live Operations');
    expect(names).toContain('Team Dashboards');
    expect(names).toContain('Trends');
    expect(names.length).toBeGreaterThan(40);
  });
});
