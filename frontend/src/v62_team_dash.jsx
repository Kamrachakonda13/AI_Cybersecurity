import React, { useEffect, useState } from 'react';
import { StatusChip } from './components/StatusChip.jsx';
import { StatusPie } from './components/StatusPie.jsx';
import { Sparkline } from './components/Sparkline.jsx';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const TEAMS = [
  { id: 'blue_team', label: 'Blue Team', domains: ['blue_team', 'network_defense'] },
  { id: 'red_team', label: 'Red Team', domains: ['red_team'] },
  { id: 'soc', label: 'SOC', domains: ['live_monitoring', 'endpoint'] },
  { id: 'ir', label: 'IR/DFIR', domains: ['dfir'] },
  { id: 'cloud', label: 'Cloud', domains: ['cloud_container'] },
  { id: 'ai', label: 'AI', domains: ['ai_agent'] },
  { id: 'supply', label: 'Supply Chain', domains: ['supply_chain'] },
  { id: 'gov', label: 'Governance', domains: ['governance', 'identity'] },
];

export function V62TeamDashView() {
  const [team, setTeam] = useState(TEAMS[0].id);
  const [checklists, setChecklists] = useState([]);
  const [runs, setRuns] = useState([]);

  const load = async () => {
    const j = await fetch(`${API}/api/v60/checklists`).then((r) => r.json()).catch(() => ({ checklists: [] }));
    setChecklists(j.checklists || []);
    const r2 = await fetch(`${API}/api/v60/runs?limit=50`).then((r) => r.json()).catch(() => []);
    setRuns(Array.isArray(r2) ? r2 : []);
  };
  useEffect(() => { load(); }, []);

  const cur = TEAMS.find((t) => t.id === team) || TEAMS[0];
  const filtered = checklists.filter((c) => cur.domains.includes(c.domain));
  // map run chip: completed -> green else amber
  const pieSegments = [
    { chip: 'green', value: runs.filter((r) => r.status === 'completed').length || 1 },
    { chip: 'amber', value: runs.filter((r) => r.status !== 'completed').length },
  ];

  return (
    <div className="content">
      <h2>Team Dashboards</h2>
      <div style={{ display: 'flex', gap: 6, marginBottom: 12, flexWrap: 'wrap' }}>
        {TEAMS.map((t) => (
          <button key={t.id} onClick={() => setTeam(t.id)} style={{ padding: '6px 10px', borderRadius: 999, border: '1px solid #e5e7eb', background: team === t.id ? '#111827' : '#fff', color: team === t.id ? '#fff' : '#111827', fontSize: 12, cursor: 'pointer' }}>{t.label}</button>
        ))}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 12 }}>
        <div style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 12, background: '#fff', textAlign: 'center' }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: '#374151' }}>{cur.label} — status</div>
          <div style={{ marginTop: 8, display: 'flex', justifyContent: 'center' }}>
            <StatusPie segments={pieSegments} size={120} />
          </div>
          <div style={{ marginTop: 8 }}>
            <Sparkline data={runs.slice(0, 12).map((_, i) => (i * 7) % 10)} width={160} height={28} />
          </div>
          <div style={{ fontSize: 11, color: '#6b7280', marginTop: 6 }}>{filtered.length} checklists · {runs.length} runs</div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 }}>
          {filtered.map((c) => (
            <div key={c.id} style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 10, background: '#fff' }}>
              <div style={{ fontWeight: 600, fontSize: 13 }}>{c.name}</div>
              <div style={{ fontSize: 11, color: '#6b7280' }}>{c.category} · {c.cadence} · {c.tier}</div>
              <div style={{ marginTop: 6 }}><StatusChip chip={c.tier === 'essential' ? 'red' : 'amber'} /></div>
            </div>
          ))}
          {filtered.length === 0 && <div style={{ fontSize: 12, color: '#6b7280' }}>No checklists for this team filter</div>}
        </div>
      </div>
    </div>
  );
}
export default V62TeamDashView;
