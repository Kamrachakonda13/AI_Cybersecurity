import React, { useEffect, useState } from 'react';
import { StatusChip } from './components/StatusChip.jsx';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const CLASS_CHIP = { 'Gen AI': 'amber', 'Agentic AI': 'red', 'Internal Tool Agent': 'green', Unknown: 'yellow' };

export function V65AgentClassificationView() {
  const [data, setData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [why, setWhy] = useState(null);

  const load = async () => {
    const r = await fetch(`${API}/api/agents/classification`);
    const j = await r.json();
    setData(j);
  };
  useEffect(() => { load(); }, []);

  const openWhy = async (agentId) => {
    setSelected(agentId);
    const r = await fetch(`${API}/api/agents/${encodeURIComponent(agentId)}/why-active`);
    const j = await r.json();
    setWhy(j);
  };

  if (!data) return <div className="content"><h2>Agent Classification</h2><div>Loading…</div></div>;

  return (
    <div className="content">
      <div className="sectionintro"><div><div className="eyebrow">AI · AGENT INTELLIGENCE</div><h2>Agents</h2><p>Why is an agent active? Classification uses recent operations + policy + traces. Active = event in last 24h or policy enabled.</p></div></div>
      <div className="cards">
        {Object.entries(data.by_class).map(([k, v]) => (
          <div key={k} className="card"><small>{k}</small><strong>{v}</strong><StatusChip chip={CLASS_CHIP[k] || 'amber'} /></div>
        ))}
        <div className="card"><small>Total agents</small><strong>{data.total_agents}</strong></div>
      </div>
      <section className="panel"><div className="panelhead"><h3>All agents (classified)</h3></div>
        <div className="table">
          {data.agents.slice(0, 30).map((a) => (
            <div key={a.agent_id} onClick={() => openWhy(a.agent_id)} className={`row clickable ${selected === a.agent_id ? 'active' : ''}`} style={{ cursor: 'pointer' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: 12 }}>{a.agent_id}</div>
                <div style={{ fontSize: 11, color: '#6b7280' }}>{a.classification} — {a.classification_reason}</div>
                <div style={{ fontSize: 10, color: '#9ca3af' }}>{a.evidence[0] || ''}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <StatusChip chip={a.is_active ? 'red' : 'green'} />
                <span style={{ fontSize: 11, color: a.is_active ? '#dc2626' : '#16a34a', fontWeight: 700 }}>{a.is_active ? 'ACTIVE' : 'IDLE'}</span>
              </div>
            </div>
          ))}
          {data.agents.length === 0 && <div className="empty">No agents observed yet — generate traffic via Tool Runner or AI Gateway /api/ai-gateway/evaluate.</div>}
        </div>
      </section>
      {why && (
        <section className="panel"><div className="panelhead"><h3>Why is “{why.agent_id}” {why.is_active ? 'ACTIVE' : 'idle'}?</h3></div><div className="callout" style={{ margin: 16 }}><b>{why.classification}</b> — {why.classification_reason}</div><ul style={{ fontSize: 11, padding: '0 24px', color: '#9eb8d4' }}>
            {why.evidence.map((e, i) => <li key={i}>{e}</li>)}
          </ul><div className="callout">Risk {why.risk_score} · Recent ops: {(why.recent_ops || []).join(', ') || '—'} · Policy enabled: {String(why.policy.enabled)}</div></section>
      )}
      <div className="helpbar">{data.note}</div>
    </div>
  );
}
export default V65AgentClassificationView;
