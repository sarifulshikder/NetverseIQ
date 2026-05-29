import React from 'react'
import clsx from 'clsx'

export default function StatCard({ label, value, icon: Icon, color = 'indigo', trend }) {
  const colors = {
    indigo: 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400',
    green:  'bg-green-50  dark:bg-green-500/10  text-green-600  dark:text-green-400',
    red:    'bg-red-50    dark:bg-red-500/10    text-red-600    dark:text-red-400',
    yellow: 'bg-yellow-50 dark:bg-yellow-500/10 text-yellow-600 dark:text-yellow-400',
    blue:   'bg-blue-50   dark:bg-blue-500/10   text-blue-600   dark:text-blue-400',
  }

  return (
    <div
      className="rounded-xl p-5 flex items-start gap-4 shadow-sm"
      style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}
    >
      <div className={clsx('w-11 h-11 rounded-lg flex items-center justify-center shrink-0', colors[color])}>
        {Icon && <Icon size={20} />}
      </div>
      <div className="min-w-0">
        <p className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>{label}</p>
        <p className="text-2xl font-bold mt-0.5" style={{ color: 'var(--text-primary)' }}>{value ?? '—'}</p>
        {trend !== undefined && (
          <p className={clsx('text-xs mt-1', trend >= 0 ? 'text-green-500' : 'text-red-500')}>
            {trend >= 0 ? '▲' : '▼'} {Math.abs(trend)}% this month
          </p>
        )}
      </div>
    </div>
  )
}
