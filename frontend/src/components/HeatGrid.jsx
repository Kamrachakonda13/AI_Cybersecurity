import React from 'react';

const CHIP_COLOR = { green: '#16a34a', amber: '#f59e0b', yellow: '#eab308', semi_red: '#f97316', red: '#dc2626' };

export function HeatGrid({ cells = [], columns = 7, cellSize = 18, gap = 3, title }) {
  if (!cells.length) return <div data-testid="heatgrid" />;
  const rows = Math.ceil(cells.length / columns);
  const w = columns * cellSize + (columns - 1) * gap;
  const h = rows * cellSize + (rows - 1) * gap;
  return (
    <svg data-testid="heatgrid" width={w} height={h} viewBox={`0 0 ${w} ${h}`} role="img" aria-label={title || 'heat grid'}>
      {cells.map((c, i) => {
        const col = i % columns;
        const row = Math.floor(i / columns);
        const x = col * (cellSize + gap);
        const y = row * (cellSize + gap);
        const chip = typeof c === 'string' ? c : c.chip || 'green';
        return <rect key={i} x={x} y={y} width={cellSize} height={cellSize} rx={3} fill={CHIP_COLOR[chip] || '#e5e7eb'} />;
      })}
    </svg>
  );
}
export default HeatGrid;
