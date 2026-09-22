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
      <h2>Security Domains — Tool Segregation (8 domains)</h2>
      <p style={{ fontSize: 12, color: '#6b7280', marginTop: -6 }}>Every tool is assigned to exactly one domain. Counts sum to 658. Vendors shown are the platforms referenced in the domain definition.</p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 12 }}>
        {stats.map((s) => (
          <div key={s.domain} onClick={() => open(s.domain)} style={{ border: selected === s.domain ? '2px solid #111827' : '1px solid #e5e7eb', borderRadius: 10, padding: 12, background: '#fff', cursor: 'pointer' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 16 }}>{DOMAIN_ICONS[s.domain] || '•'}</span>
              <StatusChip chip={s.count > 50 ? 'green' : s.count > 20 ? 'amber' : 'yellow'} />
            </div>
            <div style={{ fontWeight: 700, marginTop: 6, fontSize: 13 }}>{s.domain}</div>
            <div style={{ fontSize: 11, color: '#6b7280' }}>{s.count} tools · {Object.keys(s.categories).length} categories</div>
            <div style={{ fontSize: 10, color: '#9ca3af', marginTop: 6, lineHeight: 1.4 }}>{s.vendors.slice(0, 4).join(' · ')}</div>
            <div style={{ fontSize: 10, color: '#6b7280', marginTop: 6 }}>{Object.entries(s.categories).slice(0, 3).map(([k, v]) => `${k} ${v}`).join(' · ')}</div>
          </div>
        ))}
      </div>
      {selected && (
        <div style={{ marginTop: 16, border: '1px solid #e5e7eb', borderRadius: 10, padding: 12, background: '#fff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, fontSize: 14 }}>{selected} — {tools.length} tools</h3>
            <input placeholder="Filter tools…" value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && open(selected)} style={{ padding: '6px 8px', border: '1px solid #e5e7eb', borderRadius: 6, fontSize: 12 }} />
          </div>
          <button onClick={() => open(selected)} style={{ marginTop: 8, padding: '6px 10px', borderRadius: 6, background: '#111827', color: '#fff', fontSize: 12 }}>Search</button>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 8, marginTop: 12, maxHeight: 420, overflow: 'auto' }}>
            {tools.slice(0, 200).map((t) => (
              <div key={t.id} style={{ border: '1px solid #f3f4f6', borderRadius: 8, padding: 8, background: '#f9fafb' }}>
                <div style={{ fontWeight: 600, fontSize: 12 }}>{t.name}</div>
                <div style={{ fontSize: 10, color: '#6b7280' }}>{t.category}</div>
                <div style={{ fontSize: 10, color: '#9ca3af', marginTop: 4, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.purpose}</div>
                <div style={{ fontSize: 10, color: '#6b7280', marginTop: 4 }}>{t.execution_profile || t.access_tier}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
export default V64DomainToolsView;
