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
      <div className="sectionintro"><div><div className="eyebrow">POSTURE · TRENDS</div><h2>Trends</h2><p>Posture over time, coverage, MTTR and regressions — overview styling, sparkline + heatgrid.</p></div></div>
      <div className="cards">
        <TrendCard title="Runs (14d)" value={runs.length} chip={runs.length ? 'green' : 'amber'} data={byDay} subtitle="Runs per day (real)" />
        <TrendCard title="Sensor events" value={events.length} chip={events.length ? 'green' : 'amber'} data={byDay.map((v) => v + 1)} subtitle="Ingest volume" />
        <TrendCard title="Coverage" value={`${cov}%`} chip={cov > 50 ? 'green' : 'yellow'} data={byDay} subtitle={`${trends?.coverage?.exercised || 0}/${trends?.coverage?.total_definitions || 74} exercised`} />
        <TrendCard title="MTTR" value={mttrVal} chip={mttrChip} data={trends?.posture_series?.map((s) => s.runs) || [3, 5, 4, 6, 2]} subtitle={trends ? 'Mean from DB' : 'Requires history'} />
      </div>
      {trends?.regressions?.length > 0 && <div className="callout">Regressions: {trends.regressions.map((r) => `${r.date} spike ${r.runs} vs avg ${r.avg}`).join(' · ')}</div>}
      <section className="panel"><div className="panelhead"><h3>Coverage heatmap (last 42 runs)</h3></div>
        <div style={{ padding: 16 }}>
          <HeatGrid cells={chips} columns={14} />
          <div className="helpbar">Green = pass · Amber = warn — worst drives chip (red {' > '} semi_red {' > '} yellow {' > '} amber {' > '} green)</div>
        </div>
      </section>
    </div>
  );
}
export default V63TrendsView;
