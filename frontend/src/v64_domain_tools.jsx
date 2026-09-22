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
  const [runDialog, setRunDialog] = useState(null);
  const [runTarget, setRunTarget] = useState('');
  const [runScope, setRunScope] = useState('');

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

  const openRunDialog = (t) => {
    const admin = sessionStorage.getItem('VEYRA_admin_token') || '';
    const userToken = sessionStorage.getItem('VEYRA_user_token') || '';
    if (!admin && !userToken) { setMsg('Unlock Admin first (enter VEYRA_ADMIN_TOKEN at Admin Ethical Hacking).'); return; }
    setRunDialog(t);
    // sensible defaults per category
    const defaults = { 'Network Discovery': '10.10.20.17', 'Network Defense': '10.10.20.17', 'Wireless': 'lab-ap-01', 'Identity': '10.10.20.17', 'Cloud': 'prod-web-alb', 'Endpoint': 'web-prod-01', 'Web/API': 'http://lab-web:4101', 'AppSec': 'http://lab-web:4101', 'DFIR': 'case-001' };
    const ex = defaults[t.category] || '10.10.20.17';
    setRunTarget(ex);
    setRunScope(ex);
  };
  const runTool = async () => {
    const t = runDialog;
    if (!t || !runTarget.trim()) { setMsg('Target is required (your own asset, authorized scope only).'); return; }
    const admin = sessionStorage.getItem('VEYRA_admin_token') || '';
    const priv = sessionStorage.getItem('VEYRA_privileged_admin_token') || '';
    const userToken = sessionStorage.getItem('VEYRA_user_token') || '';
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (admin) headers['X-VEYRA-Admin-Token'] = admin;
      if (priv) headers['X-VEYRA-Privileged-Admin-Token'] = priv;
      if (userToken) headers['Authorization'] = `Bearer ${userToken}`;
      const r = await fetch(`${API}/api/admin/ethical-hacking/jobs`, { method: 'POST', headers, body: JSON.stringify({ tool: t.name, target: runTarget.trim(), scope: runScope.split(',').map(s => s.trim()).filter(Boolean), approval_ticket: `UI-${Date.now()}`, environment: 'lab', purpose: `Privileged run of ${t.name} via Domains & Tools` }) });
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || 'Failed');
      setMsg(`Staged ${t.name} → ${runTarget} as ${j.job_id} (${j.status}) — worker will execute realtime, check Tool Runner / Job queue.`);
      setRunDialog(null);
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
                <b style={{ fontSize: 12 }}>{t.name}</b><small>{t.category} · {t.purpose}</small><small style={{ marginBottom: 6, color: t.access_tier === 'privileged_admin' ? '#fbbf24' : '#778598' }}>{t.execution_profile || t.access_tier} {t.access_tier === 'privileged_admin' && '· privileged — needs privileged token'}</small>
                <button className="primary" style={{ marginTop: 'auto', padding: '6px 8px', fontSize: 11 }} onClick={() => openRunDialog(t)}>Run</button>
                <button onClick={() => openRunDialog(t)} style={{ marginTop: 6, padding: '4px 6px', fontSize: 10, background: 'transparent', border: '1px solid #1d2734', borderRadius: 6, color: '#9eb8d4' }}>Help</button>
              </div>
            ))}
          </div>
          <div className="helpbar" style={{ margin: '0 16px 16px' }}>Privileged admin can run all 658 tools realtime: stage → isolated worker claims via <code>/api/worker/jobs/next</code> (HMAC) → posts evidence. Each tool shows its <b>purpose</b> + <b>execution boundary</b> in the Help dialog.</div>
        </section>
      )}
      {runDialog && (
        <div className="overlay" onClick={() => setRunDialog(null)}><div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 640 }}>
          <div className="modalhead"><div><b>{runDialog.name}</b><small>{runDialog.category} · {runDialog.purpose} · {runDialog.execution_profile} · {runDialog.access_tier}{runDialog.access_tier === 'privileged_admin' ? ' — needs privileged token' : ''}</small><small style={{ marginTop: 8, color: '#9eb8d4' }}>{runDialog.help?.safe_workflow || runDialog.help?.summary || ''}</small></div><button className="xbtn" onClick={() => setRunDialog(null)}>✕</button></div>
          <div className="modalbody">
            <p><b>What to enter:</b></p>
            <p><b>Target</b> — the owned/authorized system under test. Examples: <code>10.10.20.17</code> (host), <code>http://lab-web:4101</code> (web/API), <code>lab-ad01</code> (AD), <code>prod-web-alb</code> (cloud). Must be in your approved scope — out-of-scope is blocked.</p>
            <p><b>Scope</b> — comma-separated authorized boundary, e.g. <code>10.10.20.0/24</code> or <code>lab</code>. Worker will refuse if target outside scope.</p>
            {runDialog.help?.expected_evidence && <p><b>Evidence you’ll get:</b> {runDialog.help.expected_evidence.join(', ')}</p>}
            {runDialog.help?.execution_boundary && <p><b>Boundary:</b> {runDialog.help.execution_boundary}</p>}
            {runDialog.help?.common_mistakes && <p><b>Common mistakes:</b> {runDialog.help.common_mistakes.join(' · ')}</p>}
            <div style={{ padding: '12px 18px', display: 'grid', gap: 8 }}>
              <input value={runTarget} onChange={(e) => setRunTarget(e.target.value)} placeholder="Target — e.g. 10.10.20.17, http://lab-web:4101, lab-ad01" style={{ padding: '10px 12px', borderRadius: 7, border: '1px solid #263342', background: '#080d14', color: '#d9e2ed' }} />
              <input value={runScope} onChange={(e) => setRunScope(e.target.value)} placeholder="Scope — e.g. 10.10.20.0/24, lab" style={{ padding: '10px 12px', borderRadius: 7, border: '1px solid #263342', background: '#080d14', color: '#d9e2ed' }} />
              <div style={{ display: 'flex', gap: 8 }}><button className="primary" onClick={runTool}>Stage job (realtime via worker)</button><button onClick={() => setRunDialog(null)}>Cancel</button></div>
            </div>
            <p style={{ color: '#667589', fontSize: 10 }}>Auth: uses your unlocked admin token + privileged admin token (if applicable) for tool execution. Passwords are for login only — not for target. Target is an IP/host, not a password.</p>
          </div>
        </div></div>
      )}
    </div>
  );
}
export default V64DomainToolsView;
