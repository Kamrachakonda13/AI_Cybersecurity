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
      <h2>Agents — Gen AI vs Agentic AI vs Internal Tool Agents</h2>
      <p style={{ fontSize: 12, color: '#6b7280', marginTop: -6 }}>Why is an agent active? Classification uses recent operations + policy + traces. Active = event in last 24h or policy enabled. Read-only, no enforcement.</p>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        {Object.entries(data.by_class).map(([k, v]) => (
          <div key={k} style={{ border: '1px solid #e5e7eb', borderRadius: 999, padding: '6px 10px', background: '#fff', fontSize: 12, display: 'flex', gap: 6, alignItems: 'center' }}>
            <StatusChip chip={CLASS_CHIP[k] || 'amber'} /> {k}: {v}
          </div>
        ))}
        <div style={{ border: '1px solid #e5e7eb', borderRadius: 999, padding: '6px 10px', background: '#f9fafb', fontSize: 12 }}>Total {data.total_agents}</div>
      </div>
      <div style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 12, background: '#fff' }}>
        <h3 style={{ margin: 0, fontSize: 13 }}>All agents (classified)</h3>
        <div style={{ marginTop: 8, display: 'grid', gap: 8 }}>
          {data.agents.slice(0, 30).map((a) => (
            <div key={a.agent_id} onClick={() => openWhy(a.agent_id)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 10px', border: '1px solid #f3f4f6', borderRadius: 8, background: selected === a.agent_id ? '#eff6ff' : '#f9fafb', cursor: 'pointer' }}>
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
          {data.agents.length === 0 && <div style={{ fontSize: 12, color: '#6b7280' }}>No agents observed yet — generate traffic via Tool Runner or AI Gateway /api/ai-gateway/evaluate.</div>}
        </div>
      </div>
      {why && (
        <div style={{ marginTop: 12, border: '1px solid #bfdbfe', borderRadius: 10, padding: 12, background: '#eff6ff' }}>
          <h3 style={{ margin: 0, fontSize: 13 }}>Why is “{why.agent_id}” {why.is_active ? 'ACTIVE' : 'idle'}?</h3>
          <div style={{ fontSize: 12, marginTop: 6, color: '#1e40af' }}>Classification: <b>{why.classification}</b> — {why.classification_reason}</div>
          <ul style={{ fontSize: 12, marginTop: 8 }}>
            {why.evidence.map((e, i) => <li key={i}>{e}</li>)}
          </ul>
          <div style={{ fontSize: 11, color: '#6b7280' }}>Risk {why.risk_score} · Recent ops: {(why.recent_ops || []).join(', ') || '—'} · Policy enabled: {String(why.policy.enabled)}</div>
        </div>
      )}
      <div style={{ marginTop: 12, fontSize: 11, color: '#6b7280' }}>{data.note}</div>
    </div>
  );
}
export default V65AgentClassificationView;
