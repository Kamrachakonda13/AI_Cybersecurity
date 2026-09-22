import React from 'react';

export function Sparkline({ data = [], width = 120, height = 32, color = '#16a34a', fill = 'rgba(22,163,74,0.12)', title }) {
  if (!data.length) return <svg data-testid="sparkline" width={width} height={height} />;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const step = width / Math.max(1, data.length - 1);
  const points = data.map((v, i) => {
    const x = i * step;
    const y = height - ((v - min) / range) * height;
    return [x, y];
  });
  const d = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  const area = `${d} L ${points[points.length - 1][0].toFixed(1)} ${height} L ${points[0][0].toFixed(1)} ${height} Z`;
  return (
    <svg data-testid="sparkline" width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title || 'sparkline'}>
      <path d={area} fill={fill} stroke="none" />
      <path d={d} fill="none" stroke={color} strokeWidth={1.5} strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}
export default Sparkline;
