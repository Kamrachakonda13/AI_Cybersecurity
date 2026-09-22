import React, { useEffect, useState } from 'react';
import { StatusChip } from './components/StatusChip.jsx';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function V60ChecklistsView() {
  const [q, setQ] = useState('');
  const [domain, setDomain] = useState('');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runMsg, setRunMsg] = useState('');
  const [recentRuns, setRecentRuns] = useState([]);
  const [approveEssential, setApproveEssential] = useState({});
  const [receipt, setReceipt] = useState(null);

  const load = async () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (domain) params.set('domain', domain);
    const r = await fetch(`${API}/api/v60/checklists?${params}`);
    const j = await r.json();
    setItems(j.checklists || []);
    setLoading(false);
    const rr = await fetch(`${API}/api/v60/runs?limit=10`).then((x) => x.json()).catch(() => []);
    setRecentRuns(Array.isArray(rr) ? rr : []);
  };
  useEffect(() => { load(); }, [domain]);

  const run = async (c) => {
    const token = sessionStorage.getItem('VEYRA_user_token');
    const isEssential = c.tier === 'essential';
    if (isEssential && !approveEssential[c.id]) {
      setRunMsg(`Approval required for essential tier — check the approval box first (governance gate).`);
      return;
    }
    const r = await fetch(`${API}/api/v60/checklists/${c.id}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify({ parameters: {}, approval_confirmed: isEssential ? !!approveEssential[c.id] : true, evidence: { source: 'console', checklist_id: c.id } }),
    });
    const j = await r.json();
    if (r.ok) {
      setRunMsg(`Run ${j.run_id}: ${j.status} — receipt ${j.receipt_sha256 ? j.receipt_sha256.slice(0, 12) : ''}… evidence & signed receipt stored.`);
      try {
        const det = await fetch(`${API}/api/v60/runs/${j.run_id}`).then((x) => x.json());
        setReceipt(det);
      } catch {}
      const rr = await fetch(`${API}/api/v60/runs?limit=10`).then((x) => x.json()).catch(() => []);
      setRecentRuns(Array.isArray(rr) ? rr : []);
    } else {
      setRunMsg(j.detail || 'Failed — approval required for essential tier');
    }
  };

  const filtered = items.filter((c) => !q || `${c.id} ${c.name} ${c.purpose}`.toLowerCase().includes(q.toLowerCase()));

  return (
    <div className="content">
      <div className="sectionintro"><div><div className="eyebrow">GOVERNANCE · 8 DOMAINS</div><h2>Checklist Library</h2><p>74 checklists across 11 domains — approve essential tier, capture evidence, signed receipt.</p></div></div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input placeholder="Search checklists…" value={q} onChange={(e) => setQ(e.target.value)} style={{ flex: 1, padding: 8, border: '1px solid #e5e7eb', borderRadius: 6 }} />
        <select value={domain} onChange={(e) => setDomain(e.target.value)} style={{ padding: 8, border: '1px solid #e5e7eb', borderRadius: 6 }}>
          <option value="">All domains</option>
          <option value="live_monitoring">live_monitoring</option>
          <option value="identity">identity</option>
          <option value="endpoint">endpoint</option>
          <option value="network_defense">network_defense</option>
          <option value="cloud_container">cloud_container</option>
          <option value="ai_agent">ai_agent</option>
          <option value="dfir">dfir</option>
          <option value="governance">governance</option>
          <option value="supply_chain">supply_chain</option>
          <option value="red_team">red_team</option>
          <option value="blue_team">blue_team</option>
        </select>
      </div>
      {runMsg && <div style={{ marginBottom: 8, padding: 8, background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 6, fontSize: 13 }}>{runMsg}</div>}
      {receipt && receipt.receipt && <div style={{ marginBottom: 8, padding: 8, background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 6, fontSize: 11, wordBreak: 'break-all' }}>Receipt {receipt.receipt.payload_sha256} — signature {receipt.receipt.signature.slice(0, 16)}… — {receipt.results?.length || 0} result(s)</div>}
      {recentRuns.length > 0 && <div style={{ marginBottom: 8, padding: 8, background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 6, fontSize: 11 }}>Recent runs: {recentRuns.slice(0, 3).map((r) => `${r.checklist_id}:${r.status}`).join(' · ')}</div>}
      {loading ? <div>Loading…</div> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
          {filtered.map((c) => (
            <div key={c.id} style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 12, background: '#fff' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: '#6b7280' }}>{c.domain} · {c.category}</span>
                <StatusChip chip={c.tier === 'essential' ? 'red' : c.tier === 'recommended' ? 'amber' : 'green'} />
              </div>
              <div style={{ fontWeight: 700, marginTop: 4 }}>{c.name}</div>
              <div style={{ fontSize: 12, color: '#4b5563', marginTop: 4 }}>{c.purpose}</div>
              <div style={{ fontSize: 11, color: '#6b7280', marginTop: 6 }}>Owner: {c.owner_role} · Cadence: {c.cadence} · Tier: {c.tier}</div>
              <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 4, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.boundary}</div>
              {c.tier === 'essential' && (
                <label style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 6, fontSize: 11 }}>
                  <input type="checkbox" checked={!!approveEssential[c.id]} onChange={(e) => setApproveEssential((s) => ({ ...s, [c.id]: e.target.checked }))} /> Approve essential run (governed)
                </label>
              )}
              <div style={{ fontSize: 11, color: '#6b7280', marginTop: 4 }}>Evidence: {c.evidence.join(', ')}</div>
              <button onClick={() => run(c)} style={{ marginTop: 8, padding: '6px 10px', borderRadius: 6, border: '1px solid #e5e7eb', background: c.tier === 'essential' ? '#7f1d1d' : '#111827', color: '#fff', fontSize: 12, cursor: 'pointer' }}>Run checklist</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
export default V60ChecklistsView;
