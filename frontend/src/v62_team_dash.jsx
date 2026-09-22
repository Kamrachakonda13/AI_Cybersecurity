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
  const pieSegments = [
    { chip: 'green', value: runs.filter((r) => r.status === 'completed').length || 1 },
    { chip: 'amber', value: runs.filter((r) => r.status !== 'completed').length },
  ];

  return (
    <div className="content">
      <div className="sectionintro"><div><div className="eyebrow">TEAM OPERATIONS</div><h2>Team Dashboards</h2><p>Status chips + pie + sparkline per team — same Overview styling, drill into checklists.</p></div></div>
      <div style={{ display: 'flex', gap: 6, marginBottom: 16, flexWrap: 'wrap' }}>
        {TEAMS.map((t) => (
          <button key={t.id} onClick={() => setTeam(t.id)} className={team === t.id ? 'primary' : ''} style={{ padding: '7px 10px', borderRadius: 6, fontSize: 11 }}>{t.label}</button>
        ))}
      </div>
      <div className="grid2">
        <section className="panel"><div className="panelhead"><h3>{cur.label} — status</h3></div>
          <div style={{ padding: 16, textAlign: 'center' }}>
            <StatusPie segments={pieSegments} size={120} />
            <div style={{ marginTop: 12 }}><Sparkline data={runs.slice(0, 12).map((_, i) => (i * 7) % 10)} width={160} height={28} /></div>
            <small style={{ color: '#778598' }}>{filtered.length} checklists · {runs.length} runs</small>
          </div>
        </section>
        <section className="panel"><div className="panelhead"><h3>{cur.label} checklists</h3></div>
          <div className="table">
            {filtered.map((c) => (
              <div key={c.id} className="row"><div><b>{c.name}</b><small>{c.category} · {c.cadence} · {c.tier}</small></div><StatusChip chip={c.tier === 'essential' ? 'red' : 'amber'} /></div>
            ))}
            {!filtered.length && <div className="empty">No checklists for this team filter</div>}
          </div>
        </section>
      </div>
    </div>
  );
}
export default V62TeamDashView;
