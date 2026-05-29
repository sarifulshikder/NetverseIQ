import React, { useEffect, useState } from 'react'
import { Puzzle, CheckCircle, XCircle, RefreshCw, ChevronRight } from 'lucide-react'
import api from '../api/client.js'
import clsx from 'clsx'

export default function Plugins() {
  const [plugins, setPlugins] = useState([])
  const [loading, setLoading] = useState(true)
  const [toggling, setToggling] = useState(null)

  const load = () => {
    setLoading(true)
    api.get('/plugins/')
      .then(r => setPlugins(r.data))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const toggle = async (plugin) => {
    setToggling(plugin.plugin_id)
    try {
      await api.patch(`/plugins/${plugin.plugin_id}`, { is_enabled: !plugin.is_enabled })
      load()
    } finally {
      setToggling(null)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          {plugins.length} plugin{plugins.length !== 1 ? 's' : ''} discovered
        </p>
        <button onClick={load}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition-colors hover:bg-gray-50 dark:hover:bg-white/5"
          style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="rounded-xl h-40 animate-pulse"
              style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }} />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {plugins.map(plugin => (
            <div key={plugin.plugin_id}
              className="rounded-xl p-5 flex flex-col gap-3 shadow-sm transition-shadow hover:shadow-md"
              style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={clsx(
                    'w-10 h-10 rounded-lg flex items-center justify-center',
                    plugin.is_enabled
                      ? 'bg-indigo-50 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400'
                      : 'bg-gray-100 dark:bg-white/5 text-gray-400'
                  )}>
                    <Puzzle size={18} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                      {plugin.name}
                    </h3>
                    <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                      v{plugin.version}
                    </span>
                  </div>
                </div>
                <span className={clsx(
                  'flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
                  plugin.is_enabled
                    ? 'bg-green-50 dark:bg-green-500/20 text-green-600 dark:text-green-400'
                    : 'bg-gray-100 dark:bg-white/10 text-gray-500'
                )}>
                  {plugin.is_enabled
                    ? <><CheckCircle size={11} /> Active</>
                    : <><XCircle size={11} /> Disabled</>
                  }
                </span>
              </div>

              <p className="text-xs flex-1 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                {plugin.description}
              </p>

              <div className="flex items-center justify-between">
                <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  by {plugin.author}
                </span>
                <button
                  onClick={() => toggle(plugin)}
                  disabled={toggling === plugin.plugin_id}
                  className={clsx(
                    'px-3 py-1.5 rounded-lg text-xs font-semibold transition-all',
                    plugin.is_enabled
                      ? 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-500/20'
                      : 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-500/20'
                  )}
                >
                  {toggling === plugin.plugin_id ? '…' : plugin.is_enabled ? 'Disable' : 'Enable'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && plugins.length === 0 && (
        <div className="rounded-xl p-12 text-center"
          style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}>
          <Puzzle size={40} className="mx-auto mb-3 text-gray-300" />
          <p className="font-medium" style={{ color: 'var(--text-primary)' }}>No plugins found</p>
          <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
            Add plugins to the <code className="bg-gray-100 dark:bg-white/10 px-1 rounded">/plugins</code> directory
          </p>
        </div>
      )}
    </div>
  )
}
