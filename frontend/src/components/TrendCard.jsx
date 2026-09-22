import React from 'react';
import { Sparkline } from './Sparkline.jsx';
import { StatusChip } from './StatusChip.jsx';

export function TrendCard({ title, value, chip = 'green', data = [], subtitle }) {
  return (
    <div data-testid="trend-card" className="card" style={{ minWidth: 160 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: '#778598', letterSpacing: 0.5 }}>{title}</span>
        <StatusChip chip={chip} size="sm" />
      </div>
      <div style={{ fontSize: 22, fontWeight: 800, color: '#e7edf5' }}>{value}</div>
      {subtitle && <div style={{ fontSize: 11, color: '#778598' }}>{subtitle}</div>}
      <div style={{ marginTop: 8 }}>
        <Sparkline data={data} width={140} height={28} />
      </div>
    </div>
  );
}
export default TrendCard;
