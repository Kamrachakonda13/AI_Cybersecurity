import React from 'react';
import { Sparkline } from './Sparkline.jsx';
import { StatusChip } from './StatusChip.jsx';

export function TrendCard({ title, value, chip = 'green', data = [], subtitle }) {
  return (
    <div data-testid="trend-card" style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 12, background: '#fff', minWidth: 160 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        <span style={{ fontSize: 12, fontWeight: 700, color: '#374151' }}>{title}</span>
        <StatusChip chip={chip} size="sm" />
      </div>
      <div style={{ fontSize: 22, fontWeight: 800, color: '#111827' }}>{value}</div>
      {subtitle && <div style={{ fontSize: 11, color: '#6b7280' }}>{subtitle}</div>}
      <div style={{ marginTop: 8 }}>
        <Sparkline data={data} width={140} height={28} />
      </div>
    </div>
  );
}
export default TrendCard;
