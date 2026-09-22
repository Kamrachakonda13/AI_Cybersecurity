import React, { useEffect, useState } from 'react';
import { StatusChip } from './components/StatusChip.jsx';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const DOMAIN_ICONS = {
  'Network Security': '🛡️',
  'Identity and Access Management': '🔑',
  'Application Security': '💻',
  'Cloud Security': '☁️',
  'Endpoint Security': '📱',
  'Security Operations & DFIR': '🔍',
  'Data Security & Cryptography': '🔒',
  'Governance, Risk & Compliance': '📋',
};

export function V64DomainToolsView() {
  const [stats, setStats] = useState([]);
  const [selected, setSelected] = useState(null);
  const [tools, setTools] = useState([]);
  const [q, setQ] = useState('');
  const [msg, setMsg] = useState('');

  useEffect(() => {
    fetch(`${API}/api/domains/overview`).then((r) => r.json()).then((j) => setStats(j.domains || [])).catch(() => {});
  }, []);

  const open = async (domain) => {
    setSelected(domain);
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    const r = await fetch(`${API}/api/domains/${encodeURIComponent(domain)}/tools?${params}`);
    const j = await r.json();
    setTools(j.tools || []);
  };

  const runTool = async (t) => {
    const admin = sessionStorage.getItem('VEYRA_admin_token') || '';
    const priv = sessionStorage.getItem('VEYRA_privileged_admin_token') || '';
    const userToken = sessionStorage.getItem('VEYRA_user_token') || '';
    if (!admin && !userToken) { setMsg('Unlock Admin first (enter VEYRA_ADMIN_TOKEN at Admin Ethical Hacking).'); return; }
    const target = window.prompt(`Target for ${t.name} (${t.category}) — e.g. 10.10.20.17, lab-web, or your own asset (authorized scope only):`, '');
    if (!target) return;
    const scope = window.prompt('Scope (comma-separated, e.g. 10.10.20.0/24 or lab scope):', target) || target;
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (admin) headers['X-VEYRA-Admin-Token'] = admin;
      if (priv) headers['X-VEYRA-Privileged-Admin-Token'] = priv;
      if (userToken) headers['Authorization'] = `Bearer ${userToken}`;
      const r = await fetch(`${API}/api/admin/ethical-hacking/jobs`, { method: 'POST', headers, body: JSON.stringify({ tool: t.name, target, scope: scope.split(',').map(s => s.trim()).filter(Boolean), approval_ticket: `UI-${Date.now()}`, environment: 'lab', purpose: `Privileged run of ${t.name} via Domains & Tools` }) });
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || 'Failed');
      setMsg(`Staged ${t.name} → ${target} as ${j.job_id} (${j.status}) — worker will execute realtime, check Tool Runner / Job queue.`);
    } catch (e) { setMsg(e.message); }
  };

  return (
    <div className="content">
      <div className="sectionintro"><div><div className="eyebrow">PLATFORM · 8 SECURITY DOMAINS</div><h2>Domains & Tools</h2><p>Every tool is assigned to exactly one domain — counts sum to 658. Click a domain to drill into its tools. As privileged admin you can <b>Run</b> any tool realtime via an isolated worker (no browser shell).</p></div></div>
      {msg && <div className="callout">{msg}</div>}
      <div className="cards">
        {stats.map((s) => (
          <div key={s.domain} onClick={() => open(s.domain)} className={`card clickable ${selected === s.domain ? 'active' : ''}`} style={{ cursor: 'pointer' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 16 }}>{DOMAIN_ICONS[s.domain] || '•'}</span>
              <StatusChip chip={s.count > 50 ? 'green' : s.count > 20 ? 'amber' : 'yellow'} />
            </div>
            <strong style={{ fontSize: 13, marginTop: 6 }}>{s.domain}</strong>
            <small>{s.count} tools · {Object.keys(s.categories).length} categories</small>
            <small style={{ lineHeight: 1.4 }}>{s.vendors.slice(0, 4).join(' · ')}</small>
            <small>{Object.entries(s.categories).slice(0, 3).map(([k, v]) => `${k} ${v}`).join(' · ')}</small>
          </div>
        ))}
      </div>
      {selected && (
        <section className="panel"><div className="panelhead"><h3>{selected} — {tools.length} tools</h3><span style={{ display: 'flex', gap: 8 }}><input placeholder="Filter…" value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && open(selected)} style={{ padding: '6px 8px', borderRadius: 6, border: '1px solid #263342', background: '#080d14', color: '#d9e2ed', fontSize: 11 }} /><button className="primary" onClick={() => open(selected)}>Search</button></span></div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 10, padding: 16, maxHeight: 520, overflow: 'auto' }}>
            {tools.slice(0, 200).map((t) => (
              <div key={t.id} className="card" style={{ padding: 12, display: 'flex', flexDirection: 'column' }}>
                <b style={{ fontSize: 12 }}>{t.name}</b><small>{t.category}</small><small style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.purpose}</small><small style={{ marginBottom: 8 }}>{t.execution_profile || t.access_tier} {t.access_tier === 'privileged_admin' && '· privileged'}</small>
                <button className="primary" style={{ marginTop: 'auto', padding: '6px 8px', fontSize: 11 }} onClick={() => runTool(t)}>Run</button>
              </div>
            ))}
          </div>
          <div className="helpbar" style={{ margin: '0 16px 16px' }}>Privileged admin (Anagha1620! + Srivallilalitha84!) can run all 658 tools realtime: stage → isolated worker claims via <code>/api/worker/jobs/next</code> (HMAC) → posts evidence to <code>/api/worker/evidence</code>. See Tool Runner for queue, Admin Ethical Hacking for high-impact gate. For production, deploy the worker (see docs below).</div>
        </section>
      )}
    </div>
  );
}
export default V64DomainToolsView;
