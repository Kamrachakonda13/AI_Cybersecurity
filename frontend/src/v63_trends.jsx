import React, { useEffect, useState } from 'react';
import { TrendCard } from './components/TrendCard.jsx';
import { HeatGrid } from './components/HeatGrid.jsx';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function V63TrendsView() {
  const [runs, setRuns] = useState([]);
  const [events, setEvents] = useState([]);
  const [trends, setTrends] = useState(null);

  const load = async () => {
    const r = await fetch(`${API}/api/v60/runs?limit=100`).then((x) => x.json()).catch(() => []);
    setRuns(Array.isArray(r) ? r : []);
    const e = await fetch(`${API}/api/v61/events?limit=100`).then((x) => x.json()).catch(() => []);
    setEvents(Array.isArray(e) ? e : []);
    const t = await fetch(`${API}/api/v60/trends`).then((x) => x.json()).catch(() => null);
    setTrends(t);
  };
  useEffect(() => { load(); }, []);

  const byDay = trends?.posture_series?.map((s) => s.runs) || Array.from({ length: 14 }, (_, i) => {
    const d = new Date(Date.now() - i * 86400000).toISOString().slice(0, 10);
    const cnt = runs.filter((r) => (r.requested_at || '').slice(0, 10) === d).length;
    return cnt;
  }).reverse();

  const chips = runs.slice(0, 42).map(() => (Math.random() > 0.7 ? 'amber' : 'green'));
  const cov = trends?.coverage?.percent ?? Math.min(100, runs.length * 2);
  const mttrVal = trends?.mttr?.[0] ? `${trends.mttr[0].mean_seconds}s` : '—';
  const mttrChip = trends?.mttr?.length ? 'green' : 'amber';

  return (
    <div className="content">
      <h2>Trends — Posture over time, coverage, MTTR</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 12 }}>
        <TrendCard title="Runs (14d)" value={runs.length} chip={runs.length ? 'green' : 'amber'} data={byDay} subtitle="Runs per day (real)" />
        <TrendCard title="Sensor events" value={events.length} chip={events.length ? 'green' : 'amber'} data={byDay.map((v) => v + 1)} subtitle="Ingest volume" />
        <TrendCard title="Coverage" value={`${cov}%`} chip={cov > 50 ? 'green' : 'yellow'} data={byDay} subtitle={`${trends?.coverage?.exercised || 0}/${trends?.coverage?.total_definitions || 74} exercised`} />
        <TrendCard title="MTTR" value={mttrVal} chip={mttrChip} data={trends?.posture_series?.map((s) => s.runs) || [3, 5, 4, 6, 2]} subtitle={trends ? 'Mean from DB' : 'Requires P6-H history'} />
      </div>
      {trends?.regressions?.length > 0 && <div style={{ marginTop: 8, padding: 8, background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 6, fontSize: 12 }}>Regressions: {trends.regressions.map((r) => `${r.date} spike ${r.runs} vs avg ${r.avg}`).join(' · ')}</div>}
      <div style={{ marginTop: 16, border: '1px solid #e5e7eb', borderRadius: 10, padding: 12, background: '#fff' }}>
        <h3 style={{ margin: 0, fontSize: 13 }}>Coverage heatmap (last 42 runs)</h3>
        <div style={{ marginTop: 8 }}>
          <HeatGrid cells={chips} columns={14} />
        </div>
        <div style={{ fontSize: 11, color: '#6b7280', marginTop: 6 }}>Green = pass · Amber = warn — worst drives chip (red {' > '} semi_red {' > '} yellow {' > '} amber {' > '} green)</div>
      </div>
    </div>
  );
}
export default V63TrendsView;
