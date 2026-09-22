import React from 'react';

const CHIP_COLOR = {
  green: '#16a34a',
  amber: '#f59e0b',
  yellow: '#eab308',
  semi_red: '#f97316',
  red: '#dc2626',
};

// Pure SVG pie; segments = [{chip, value}]
export function StatusPie({ segments = [], size = 120, hole = 0.55, title }) {
  const total = segments.reduce((s, x) => s + (x.value || 0), 0) || 1;
  let angle = -90;
  const r = size / 2;
  const cx = r, cy = r;
  const inner = r * hole;
  const arcs = segments.map((seg) => {
    const sweep = (seg.value / total) * 360;
    const start = angle;
    const end = angle + sweep;
    angle = end;
    const large = sweep > 180 ? 1 : 0;
    const rad = (deg) => (deg * Math.PI) / 180;
    const x1 = cx + r * Math.cos(rad(start));
    const y1 = cy + r * Math.sin(rad(start));
    const x2 = cx + r * Math.cos(rad(end));
    const y2 = cy + r * Math.sin(rad(end));
    const xi1 = cx + inner * Math.cos(rad(end));
    const yi1 = cy + inner * Math.sin(rad(end));
    const xi2 = cx + inner * Math.cos(rad(start));
    const yi2 = cy + inner * Math.sin(rad(start));
    const d = `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} L ${xi1} ${yi1} A ${inner} ${inner} 0 ${large} 0 ${xi2} ${yi2} Z`;
    return { d, color: CHIP_COLOR[seg.chip] || '#6b7280', seg };
  });
  return (
    <svg data-testid="status-pie" width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={title || 'status pie'}>
      {arcs.map((a, i) => (
        <path key={i} d={a.d} fill={a.color} stroke="#fff" strokeWidth={1} />
      ))}
      <circle cx={cx} cy={cy} r={inner - 1} fill="#fff" />
      <text x={cx} y={cy + 4} textAnchor="middle" fontSize={12} fontWeight={700} fill="#111827">{total}</text>
    </svg>
  );
}
export default StatusPie;
