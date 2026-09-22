import React from 'react';

export function DropTimeline({ drops = [], width = 320, height = 48 }) {
  if (!drops.length) return <div data-testid="drop-timeline" style={{ width, height, background: '#f3f4f6', borderRadius: 6 }} />;
  const times = drops.map((d) => new Date(d.drop_time || d.created_at || Date.now()).getTime());
  const min = Math.min(...times);
  const max = Math.max(...times, min + 1);
  const range = max - min;
  return (
    <svg data-testid="drop-timeline" width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label="drop timeline">
      <line x1={0} y1={height / 2} x2={width} y2={height / 2} stroke="#e5e7eb" strokeWidth={2} />
      {drops.map((d, i) => {
        const t = new Date(d.drop_time || d.created_at).getTime();
        const x = ((t - min) / range) * (width - 12) + 6;
        const y = height / 2;
        const color = d.link_type === 'ethernet' ? '#2563eb' : '#dc2626';
        return <g key={d.drop_id || i}><circle cx={x} cy={y} r={6} fill={color} stroke="#fff" strokeWidth={2} /><title>{d.link_id}</title></g>;
      })}
    </svg>
  );
}
export default DropTimeline;
