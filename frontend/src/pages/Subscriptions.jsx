import React, { useEffect, useState, useCallback } from 'react'
import { PlusCircle, RefreshCw, Trash2, Edit2, RotateCcw, PauseCircle } from 'lucide-react'
import api from '../api/client.js'
import clsx from 'clsx'

const STATUS_STYLES = {
  active:    'bg-green-50 dark:bg-green-500/20 text-green-600 dark:text-green-400',
  suspended: 'bg-red-50 dark:bg-red-500/20 text-red-600 dark:text-red-400',
  expired:   'bg-gray-100 dark:bg-white/10 text-gray-500',
  pending:   'bg-yellow-50 dark:bg-yellow-500/20 text-yellow-600 dark:text-yellow-400',
}

const EMPTY_FORM = {
  customer_id: '', package_id: '', status: 'active',
  start_date: new Date().toISOString().slice(0,10),
  end_date: '', monthly_price: 0, auto_renew: true, connection_details: '',
}

export default function Subscriptions() {
  const [subs, setSubs]       = useState([])
  const [total, setTotal]     = useState(0)
  const [loading, setLoading] = useState(true)
  const [modal, setModal]     = useState(null)
  const [form, setForm]       = useState(EMPTY_FORM)
  const [saving, setSaving]   = useState(false)
  const [error, setError]     = useState('')
  const [filter, setFilter]   = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const r = await api.get(`/p/subscription/list?limit=100${filter ? `&status=${filter}` : ''}`)
      setSubs(r.data.items || [])
      setTotal(r.data.total || 0)
    } catch { setSubs([]) }
    finally { setLoading(false) }
  }, [filter])

  useEffect(() => { load() }, [load])

  const openAdd  = () => { setForm(EMPTY_FORM); setError(''); setModal('add') }
  const openEdit = (s) => { setForm({ ...s, start_date: s.start_date?.slice(0,10), end_date: s.end_date?.slice(0,10) || '' }); setError(''); setModal(s) }

  const save = async () => {
    setSaving(true); setError('')
    try {
      const payload = { ...form, customer_id: parseInt(form.customer_id), package_id: parseInt(form.package_id), monthly_price: parseFloat(form.monthly_price) }
      if (modal === 'add') await api.post('/p/subscription/', payload)
      else await api.put(`/p/subscription/${modal.id}`, payload)
      setModal(null); load()
    } catch (e) { setError(e.response?.data?.detail || 'Save failed') }
    finally { setSaving(false) }
  }

  const del = async (id) => {
    if (!confirm('Delete this subscription?')) return
    await api.delete(`/p/subscription/${id}`)
    load()
  }

  const renew = async (id) => {
    await api.post(`/p/subscription/${id}/renew?months=1`)
    load()
  }

  const suspend = async (id) => {
    await api.post(`/p/subscription/${id}/suspend`)
    load()
  }

  const f = (k, v) => setForm(p => ({ ...p, [k]: v }))

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <select value={filter} onChange={e => setFilter(e.target.value)}
          className="px-3 py-2 text-sm rounded-lg border outline-none focus:ring-2 focus:ring-indigo-500
            bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
          <option value="">All Status</option>
          {['active','suspended','expired','pending'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <button onClick={load} className="p-2 rounded-lg border hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
          style={{ borderColor: 'var(--border)' }}>
          <RefreshCw size={15} className={clsx('text-gray-400', loading && 'animate-spin')} />
        </button>
        <button onClick={openAdd}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium transition-colors">
          <PlusCircle size={15} /> Add Subscription
        </button>
      </div>

      {/* Table */}
      <div className="rounded-xl overflow-hidden shadow-sm"
        style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}>
        <div className="px-5 py-3 border-b flex items-center justify-between"
          style={{ borderColor: 'var(--border)' }}>
          <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
            Subscriptions <span className="text-gray-400 font-normal">({total})</span>
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b" style={{ borderColor: 'var(--border)' }}>
                {['Customer ID','Package ID','Status','Monthly Price','Start Date','End Date','Auto Renew','Actions'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>Loading…</td></tr>
              ) : subs.length === 0 ? (
                <tr><td colSpan={8} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>No subscriptions found</td></tr>
              ) : subs.map(s => (
                <tr key={s.id} className="border-b last:border-0 hover:bg-gray-50 dark:hover:bg-white/3 transition-colors"
                  style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-3 font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>{s.customer_id}</td>
                  <td className="px-4 py-3 font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>{s.package_id}</td>
                  <td className="px-4 py-3">
                    <span className={clsx('px-2 py-0.5 rounded-full text-xs font-medium', STATUS_STYLES[s.status] || STATUS_STYLES.pending)}>
                      {s.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-semibold" style={{ color: 'var(--text-primary)' }}>৳{s.monthly_price}</td>
                  <td className="px-4 py-3 text-xs" style={{ color: 'var(--text-secondary)' }}>{s.start_date ? new Date(s.start_date).toLocaleDateString() : '—'}</td>
                  <td className="px-4 py-3 text-xs" style={{ color: 'var(--text-secondary)' }}>{s.end_date ? new Date(s.end_date).toLocaleDateString() : '—'}</td>
                  <td className="px-4 py-3 text-xs" style={{ color: 'var(--text-secondary)' }}>{s.auto_renew ? '✓' : '✗'}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button onClick={() => openEdit(s)} title="Edit" className="p-1.5 rounded hover:bg-indigo-50 dark:hover:bg-indigo-500/10 text-indigo-500 transition-colors"><Edit2 size={13} /></button>
                      <button onClick={() => renew(s.id)} title="Renew 1 month" className="p-1.5 rounded hover:bg-green-50 dark:hover:bg-green-500/10 text-green-500 transition-colors"><RotateCcw size={13} /></button>
                      <button onClick={() => suspend(s.id)} title="Suspend" className="p-1.5 rounded hover:bg-yellow-50 dark:hover:bg-yellow-500/10 text-yellow-500 transition-colors"><PauseCircle size={13} /></button>
                      <button onClick={() => del(s.id)} title="Delete" className="p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-500/10 text-red-400 transition-colors"><Trash2 size={13} /></button>
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
          <div className="w-full max-w-lg rounded-2xl shadow-2xl overflow-y-auto max-h-[90vh]"
            style={{ background: 'var(--bg-secondary)' }}>
            <div className="flex items-center justify-between px-6 py-4 border-b" style={{ borderColor: 'var(--border)' }}>
              <h2 className="font-bold" style={{ color: 'var(--text-primary)' }}>
                {modal === 'add' ? 'Add Subscription' : 'Edit Subscription'}
              </h2>
              <button onClick={() => setModal(null)} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">×</button>
            </div>
            <div className="p-6 grid grid-cols-2 gap-4">
              {[
                ['customer_id','Customer ID','number'], ['package_id','Package ID','number'],
                ['monthly_price','Monthly Price (৳)','number'], ['connection_details','Connection Details','text'],
                ['start_date','Start Date','date'], ['end_date','End Date','date'],
              ].map(([key, label, type]) => (
                <div key={key} className={key === 'connection_details' ? 'col-span-2' : ''}>
                  <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>{label}</label>
                  <input type={type} value={form[key] ?? ''} onChange={e => f(key, e.target.value)}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                      bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100" />
                </div>
              ))}
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>Status</label>
                <select value={form.status} onChange={e => f('status', e.target.value)}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
                  {['active','suspended','expired','pending'].map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="flex items-center gap-3 pt-5">
                <input type="checkbox" id="auto_renew" checked={!!form.auto_renew} onChange={e => f('auto_renew', e.target.checked)}
                  className="w-4 h-4 accent-indigo-600" />
                <label htmlFor="auto_renew" className="text-sm" style={{ color: 'var(--text-primary)' }}>Auto Renew</label>
              </div>
            </div>
            {error && <p className="px-6 pb-2 text-red-500 text-sm">{error}</p>}
            <div className="flex justify-end gap-3 px-6 py-4 border-t" style={{ borderColor: 'var(--border)' }}>
              <button onClick={() => setModal(null)} className="px-4 py-2 rounded-lg text-sm border transition-colors hover:bg-gray-50 dark:hover:bg-white/5"
                style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>Cancel</button>
              <button onClick={save} disabled={saving}
                className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold transition-colors disabled:opacity-60">
                {saving ? 'Saving…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
