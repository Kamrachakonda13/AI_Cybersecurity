import React from 'react';

export function Sparkbar({ data = [], width = 120, height = 32, color = '#2563eb', title }) {
  if (!data.length) return <svg data-testid="sparkbar" width={width} height={height} />;
  const max = Math.max(...data, 1);
  const gap = 2;
  const bw = (width - gap * (data.length - 1)) / data.length;
  return (
    <svg data-testid="sparkbar" width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title || 'sparkbar'}>
      {data.map((v, i) => {
        const h = (v / max) * height;
        const x = i * (bw + gap);
        const y = height - h;
        return <rect key={i} x={x} y={y} width={bw} height={h} rx={2} fill={color} opacity={0.85} />;
      })}
    </svg>
  );
}
export default Sparkbar;
