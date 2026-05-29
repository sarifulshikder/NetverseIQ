import React, { useEffect, useState, useCallback } from 'react'
import { Ticket, Search, RefreshCw, Trash2, Edit2, AlertCircle, Clock, CheckCircle2, MessageSquarePlus } from 'lucide-react'
import api from '../api/client.js'
import clsx from 'clsx'

const STATUS_STYLES = {
  open:        'bg-blue-50 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400',
  in_progress: 'bg-yellow-50 dark:bg-yellow-500/20 text-yellow-600 dark:text-yellow-400',
  resolved:    'bg-green-50 dark:bg-green-500/20 text-green-600 dark:text-green-400',
  closed:      'bg-gray-100 dark:bg-white/10 text-gray-500',
}

const PRIORITY_STYLES = {
  low:    'text-gray-500',
  medium: 'text-blue-500',
  high:   'text-orange-500',
  urgent: 'text-red-500 font-bold',
}

const EMPTY_FORM = {
  customer_id: '', customer_name: '', subject: '', description: '',
  priority: 'medium', status: 'open', category: 'technical', assigned_to: ''
}

export default function Support() {
  const [tickets, setTickets] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState(null) // null | 'add' | {ticket}
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [stats, setStats] = useState({ total_tickets: 0, open_tickets: 0, urgent_tickets: 0 })

  const loadStats = async () => {
    try {
      const r = await api.get('/p/support/stats')
      setStats(r.data)
    } catch {}
  }

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const r = await api.get('/p/support/tickets?limit=100')
      setTickets(r.data.items || [])
      setTotal(r.data.total || 0)
    } catch {
      setTickets([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load(); loadStats() }, [load])

  const openAdd = () => { setForm(EMPTY_FORM); setError(''); setModal('add') }
  const openEdit = (t) => { setForm({ ...t }); setError(''); setModal(t) }

  const save = async () => {
    setSaving(true); setError('')
    try {
      if (modal === 'add') {
        await api.post('/p/support/tickets', form)
      } else {
        await api.put(`/p/support/tickets/${modal.id}`, form)
      }
      setModal(null); load(); loadStats()
    } catch (e) {
      setError(e.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Tickets', value: stats.total_tickets, icon: Ticket, color: 'text-indigo-600' },
          { label: 'Open', value: stats.open_tickets, icon: Clock, color: 'text-blue-600' },
          { label: 'In Progress', value: stats.in_progress, icon: RefreshCw, color: 'text-yellow-600' },
          { label: 'Urgent', value: stats.urgent_tickets, icon: AlertCircle, color: 'text-red-600' },
        ].map((s, i) => (
          <div key={i} className="p-4 rounded-xl shadow-sm border" style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>{s.label}</p>
                <p className="text-2xl font-bold mt-1" style={{ color: 'var(--text-primary)' }}>{s.value || 0}</p>
              </div>
              <div className={clsx('p-2 rounded-lg bg-opacity-10', s.color.replace('text-', 'bg-'))}>
                <s.icon size={20} className={s.color} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            placeholder="Search tickets…"
            className="w-full pl-9 pr-4 py-2 text-sm rounded-lg border outline-none focus:ring-2 focus:ring-indigo-500
              bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <button onClick={() => { load(); loadStats() }} className="p-2 rounded-lg border hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
          style={{ borderColor: 'var(--border)' }}>
          <RefreshCw size={15} className={clsx('text-gray-400', loading && 'animate-spin')} />
        </button>
        <button onClick={openAdd}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium transition-colors">
          <MessageSquarePlus size={15} /> New Ticket
        </button>
      </div>

      {/* Table */}
      <div className="rounded-xl overflow-hidden shadow-sm border"
        style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b" style={{ borderColor: 'var(--border)' }}>
                {['ID', 'Customer', 'Subject', 'Priority', 'Status', 'Date', 'Actions'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>Loading…</td></tr>
              ) : tickets.length === 0 ? (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>No tickets found</td></tr>
              ) : tickets.map(t => (
                <tr key={t.id} className="border-b last:border-0 hover:bg-gray-50 dark:hover:bg-white/3 transition-colors"
                  style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-3 text-xs font-mono text-gray-400">#{t.id}</td>
                  <td className="px-4 py-3">
                    <div className="font-medium" style={{ color: 'var(--text-primary)' }}>{t.customer_name}</div>
                    <div className="text-[10px] text-gray-400 uppercase font-semibold tracking-tight">ID: {t.customer_id}</div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-medium max-w-[200px] truncate" style={{ color: 'var(--text-primary)' }}>{t.subject}</div>
                    <div className="text-xs text-gray-400 truncate max-w-[200px]">{t.category}</div>
                  </td>
                  <td className="px-4 py-3 text-xs">
                    <span className={clsx('uppercase tracking-wider font-semibold', PRIORITY_STYLES[t.priority])}>
                      {t.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={clsx('px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider', STATUS_STYLES[t.status] || STATUS_STYLES.open)}>
                      {t.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs" style={{ color: 'var(--text-secondary)' }}>
                    {new Date(t.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center gap-1 justify-end">
                      <button onClick={() => openEdit(t)} className="p-1.5 rounded hover:bg-indigo-50 dark:hover:bg-indigo-500/10 text-indigo-500 transition-colors">
                        <Edit2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {modal !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden"
            style={{ background: 'var(--bg-secondary)' }}>
            <div className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: 'var(--border)' }}>
              <h2 className="font-bold" style={{ color: 'var(--text-primary)' }}>
                {modal === 'add' ? 'Open New Ticket' : 'Update Ticket'}
              </h2>
              <button onClick={() => setModal(null)} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">×</button>
            </div>
            <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-1">
                  <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Customer ID</label>
                  <input type="number" value={form.customer_id} required
                    onChange={e => setForm(f => ({ ...f, customer_id: parseInt(e.target.value) || '' }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                      bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div className="col-span-1">
                  <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Customer Name</label>
                  <input value={form.customer_name}
                    onChange={e => setForm(f => ({ ...f, customer_name: e.target.value }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                      bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Subject</label>
                <input value={form.subject} required
                  onChange={e => setForm(f => ({ ...f, subject: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Description</label>
                <textarea value={form.description} rows={4} required
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500 resize-none
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100" />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Priority</label>
                  <select value={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                    {['low','medium','high','urgent'].map(p => <option key={p} value={p}>{p}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Status</label>
                  <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                    {['open','in_progress','resolved','closed'].map(s => <option key={s} value={s}>{s.replace('_',' ')}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Category</label>
                  <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                    {['technical','billing','general','sales'].map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Assigned To</label>
                <input value={form.assigned_to || ''}
                  onChange={e => setForm(f => ({ ...f, assigned_to: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
            </div>
            {error && <p className="px-6 pb-4 text-red-500 text-xs font-medium">{error}</p>}
            <div className="flex justify-end gap-3 px-6 py-4 border-t bg-gray-50 dark:bg-gray-900/50" style={{ borderColor: 'var(--border)' }}>
              <button onClick={() => setModal(null)} className="px-4 py-2 rounded-lg text-sm border hover:bg-white dark:hover:bg-white/5 transition-colors"
                style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>Cancel</button>
              <button onClick={save} disabled={saving}
                className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold transition-colors disabled:opacity-60">
                {saving ? 'Saving…' : 'Save Ticket'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
