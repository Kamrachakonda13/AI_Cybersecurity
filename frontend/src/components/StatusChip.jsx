import React from 'react';

const COLORS = {
  green: { bg: '#16a34a', fg: '#fff', label: 'GREEN', icon: '✓' },
  amber: { bg: '#f59e0b', fg: '#111827', label: 'AMBER', icon: '⚠' },
  yellow: { bg: '#eab308', fg: '#111827', label: 'YELLOW', icon: '⚠' },
  semi_red: { bg: '#f97316', fg: '#fff', label: 'SEMI_RED', icon: '⚠' },
  red: { bg: '#dc2626', fg: '#fff', label: 'RED', icon: '✗' },
};

export function StatusChip({ chip = 'green', size = 'sm', pulse = false, title }) {
  const c = COLORS[chip] || COLORS.green;
  const pad = size === 'sm' ? '2px 8px' : size === 'lg' ? '6px 14px' : '4px 10px';
  const fs = size === 'sm' ? 12 : size === 'lg' ? 14 : 13;
  return (
    <span
      data-testid="status-chip"
      data-chip={chip}
      title={title || `${c.label}: ${chip}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: pad,
        borderRadius: 999,
        background: c.bg,
        color: c.fg,
        fontSize: fs,
        fontWeight: 700,
        letterSpacing: 0.3,
        border: chip === 'red' ? '1px solid #991b1b' : '1px solid rgba(0,0,0,0.08)',
        boxShadow: pulse && chip === 'red' ? '0 0 0 3px rgba(220,38,38,0.25)' : 'none',
      }}
    >
      <span aria-hidden>{c.icon}</span>
      {c.label}
    </span>
  );
}

export const CHIP_ORDER = ['green', 'amber', 'yellow', 'semi_red', 'red'];
export default StatusChip;
