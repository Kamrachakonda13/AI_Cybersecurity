import React, { useEffect, useState } from 'react';
import { StatusChip } from './components/StatusChip.jsx';
import { DropTimeline } from './components/DropTimeline.jsx';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function V61LiveOpsView() {
  const [events, setEvents] = useState([]);
  const [drops, setDrops] = useState([]);
  const [baselines, setBaselines] = useState([]);

  const load = async () => {
    const [e, d, b] = await Promise.all([
      fetch(`${API}/api/v61/events?limit=30`).then((r) => r.json()).catch(() => []),
      fetch(`${API}/api/v61/drops?limit=20`).then((r) => r.json()).catch(() => []),
      fetch(`${API}/api/v61/baselines?limit=20`).then((r) => r.json()).catch(() => []),
    ]);
    setEvents(Array.isArray(e) ? e : []);
    setDrops(Array.isArray(d) ? d : []);
    setBaselines(Array.isArray(b) ? b : []);
  };
  useEffect(() => { load(); const t = setInterval(load, 15000); return () => clearInterval(t); }, []);

  return (
    <div className="content">
      <h2>Live Operations — Wi-Fi / Ethernet / Devices / Drops</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 12, background: '#fff' }}>
          <h3 style={{ margin: 0, fontSize: 13 }}>Sensor Events (last 30)</h3>
          {events.length === 0 ? <div style={{ fontSize: 12, color: '#6b7280', marginTop: 8 }}>No events — ingest via POST /api/v61/ingest (token-gated)</div> : (
            <div style={{ marginTop: 8 }}>
              {events.slice(0, 10).map((ev) => (
                <div key={ev.event_id} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>
                  <span>{ev.sensor_type}:{ev.event_type}</span>
                  <StatusChip chip={ev.severity === 'CRITICAL' ? 'red' : ev.severity === 'HIGH' ? 'semi_red' : 'green'} />
                </div>
              ))}
            </div>
          )}
        </div>
        <div style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 12, background: '#fff' }}>
          <h3 style={{ margin: 0, fontSize: 13 }}>Baselines</h3>
          {baselines.length === 0 ? <div style={{ fontSize: 12, color: '#6b7280', marginTop: 8 }}>No baselines — create via POST /api/v61/baselines</div> : (
            <div style={{ marginTop: 8 }}>
              {baselines.slice(0, 8).map((b) => (
                <div key={b.baseline_id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, padding: '4px 0' }}>
                  <span>{b.scope} ({b.version})</span>
                  <StatusChip chip={b.approved ? 'green' : 'amber'} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      <div style={{ marginTop: 12, border: '1px solid #e5e7eb', borderRadius: 10, padding: 12, background: '#fff' }}>
        <h3 style={{ margin: 0, fontSize: 13 }}>Drop Timeline</h3>
        <div style={{ marginTop: 8 }}>
          <DropTimeline drops={drops} width={640} />
        </div>
        {drops.slice(0, 5).map((d) => (
          <div key={d.drop_id} style={{ fontSize: 12, padding: '4px 0', borderBottom: '1px solid #f3f4f6' }}>
            <span style={{ fontWeight: 600 }}>{d.link_id}</span> · {d.link_type} — {(d.hypotheses || []).map((h) => h.cause).join(', ')}
          </div>
        ))}
      </div>
    </div>
  );
}
export default V61LiveOpsView;
