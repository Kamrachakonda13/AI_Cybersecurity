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
      <div className="sectionintro"><div><div className="eyebrow">LIVE TELEMETRY · TOKEN-GATED</div><h2>Live Operations</h2><p>Wi-Fi / Ethernet / device joins & drop diagnosis — provenance + SHA-256, no deauth.</p></div></div>
      <div className="grid2">
        <section className="panel"><div className="panelhead"><h3>Sensor Events (last 30)</h3></div>
          <div className="table">
            {events.length === 0 ? <div className="empty">No events — ingest via POST /api/v61/ingest (token-gated)</div> :
              events.slice(0, 10).map((ev) => (
                <div key={ev.event_id} className="row"><div><b>{ev.sensor_type}:{ev.event_type}</b><small>{ev.event_id.slice(0, 12)}</small></div><StatusChip chip={ev.severity === 'CRITICAL' ? 'red' : ev.severity === 'HIGH' ? 'semi_red' : 'green'} /></div>
              ))}
          </div>
        </section>
        <section className="panel"><div className="panelhead"><h3>Baselines</h3></div>
          <div className="table">
            {baselines.length === 0 ? <div className="empty">No baselines — create via POST /api/v61/baselines</div> :
              baselines.slice(0, 8).map((b) => (
                <div key={b.baseline_id} className="row"><div><b>{b.scope}</b><small>{b.version} · {b.owner}</small></div><StatusChip chip={b.approved ? 'green' : 'amber'} /></div>
              ))}
          </div>
        </section>
      </div>
      <section className="panel"><div className="panelhead"><h3>Drop Timeline</h3></div>
        <div style={{ padding: 16 }}>
          <DropTimeline drops={drops} width={640} />
          <div className="table">
            {drops.slice(0, 5).map((d) => (
              <div key={d.drop_id} className="row"><div><b>{d.link_id}</b><small>{d.link_type} — {(d.hypotheses || []).map((h) => h.cause).join(', ')}</small></div></div>
            ))}
            {!drops.length && <div className="empty">No drops recorded</div>}
          </div>
        </div>
      </section>
    </div>
  );
}
export default V61LiveOpsView;
