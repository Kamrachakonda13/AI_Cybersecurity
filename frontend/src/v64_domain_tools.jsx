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

  return (
    <div className="content">
      <div className="sectionintro"><div><div className="eyebrow">PLATFORM · 8 SECURITY DOMAINS</div><h2>Domains & Tools</h2><p>Every tool is assigned to exactly one domain — counts sum to 658. Click a domain to drill into its tools.</p></div></div>
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
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 10, padding: 16, maxHeight: 420, overflow: 'auto' }}>
            {tools.slice(0, 200).map((t) => (
              <div key={t.id} className="card" style={{ padding: 12 }}>
                <b style={{ fontSize: 12 }}>{t.name}</b><small>{t.category}</small><small style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.purpose}</small><small>{t.execution_profile || t.access_tier}</small>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
export default V64DomainToolsView;
