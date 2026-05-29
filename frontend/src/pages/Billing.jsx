import React, { useEffect, useState, useCallback } from 'react'
import { PlusCircle, RefreshCw, Trash2, Edit2, DollarSign } from 'lucide-react'
import api from '../api/client.js'
import StatCard from '../components/StatCard.jsx'
import clsx from 'clsx'

const STATUS_STYLES = {
  paid:      'bg-green-50 dark:bg-green-500/20 text-green-600 dark:text-green-400',
  unpaid:    'bg-red-50 dark:bg-red-500/20 text-red-500 dark:text-red-400',
  partial:   'bg-yellow-50 dark:bg-yellow-500/20 text-yellow-600 dark:text-yellow-400',
  cancelled: 'bg-gray-100 dark:bg-white/10 text-gray-500',
}

const EMPTY_FORM = {
  customer_id: '', customer_name: '', amount: 0,
  discount: 0, tax: 0, status: 'unpaid',
  payment_method: '', notes: '',
}

export default function Billing() {
  const [invoices, setInvoices] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [inv, st] = await Promise.all([
        api.get('/p/billing/invoices?limit=100'),
        api.get('/p/billing/stats'),
      ])
      setInvoices(inv.data.items || [])
      setStats(st.data)
    } catch { setInvoices([]) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const save = async () => {
    setSaving(true); setError('')
    try {
      if (modal === 'add') await api.post('/p/billing/invoices', form)
      else await api.put(`/p/billing/invoices/${modal.id}`, form)
      setModal(null); load()
    } catch (e) { setError(e.response?.data?.detail || 'Save failed') }
    finally { setSaving(false) }
  }

  const del = async (id) => {
    if (!confirm('Delete this invoice?')) return
    await api.delete(`/p/billing/invoices/${id}`)
    load()
  }

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Invoices" value={stats?.total_invoices ?? '…'} icon={DollarSign} color="indigo" />
        <StatCard label="Paid"           value={stats?.paid ?? '…'} icon={DollarSign} color="green" />
        <StatCard label="Unpaid"         value={stats?.unpaid ?? '…'} icon={DollarSign} color="red" />
        <StatCard label="Total Revenue"  value={`৳${(stats?.total_revenue ?? 0).toLocaleString()}`} icon={DollarSign} color="blue" />
      </div>

      <div className="flex justify-end">
        <button onClick={() => { setForm(EMPTY_FORM); setError(''); setModal('add') }}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium">
          <PlusCircle size={15} /> New Invoice
        </button>
      </div>

      <div className="rounded-xl overflow-hidden shadow-sm"
        style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b" style={{ borderColor: 'var(--border)' }}>
                {['Invoice #','Customer','Amount','Total','Status','Method','Actions'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>Loading…</td></tr>
              ) : invoices.length === 0 ? (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>No invoices yet</td></tr>
              ) : invoices.map(inv => (
                <tr key={inv.id} className="border-b last:border-0 hover:bg-gray-50 dark:hover:bg-white/3"
                  style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-3 font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>{inv.invoice_number}</td>
                  <td className="px-4 py-3" style={{ color: 'var(--text-primary)' }}>{inv.customer_name || `#${inv.customer_id}`}</td>
                  <td className="px-4 py-3" style={{ color: 'var(--text-secondary)' }}>৳{inv.amount}</td>
                  <td className="px-4 py-3 font-bold" style={{ color: 'var(--text-primary)' }}>৳{inv.total}</td>
                  <td className="px-4 py-3">
                    <span className={clsx('px-2 py-0.5 rounded-full text-xs font-medium', STATUS_STYLES[inv.status] || STATUS_STYLES.unpaid)}>
                      {inv.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs" style={{ color: 'var(--text-secondary)' }}>{inv.payment_method || '—'}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button onClick={() => { setForm({ ...inv }); setError(''); setModal(inv) }}
                        className="p-1.5 rounded hover:bg-indigo-50 dark:hover:bg-indigo-500/10 text-indigo-500">
                        <Edit2 size={13} />
                      </button>
                      <button onClick={() => del(inv.id)}
                        className="p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-500/10 text-red-400">
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {modal !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl shadow-2xl" style={{ background: 'var(--bg-secondary)' }}>
            <div className="flex items-center justify-between px-6 py-4 border-b" style={{ borderColor: 'var(--border)' }}>
              <h2 className="font-bold" style={{ color: 'var(--text-primary)' }}>
                {modal === 'add' ? 'New Invoice' : 'Edit Invoice'}
              </h2>
              <button onClick={() => setModal(null)} className="text-gray-400 text-2xl leading-none">×</button>
            </div>
            <div className="p-6 grid grid-cols-2 gap-4">
              {[
                ['customer_id','Customer ID','number'], ['customer_name','Customer Name','text'],
                ['amount','Amount (৳)','number'], ['discount','Discount (৳)','number'],
                ['tax','Tax (৳)','number'],
              ].map(([k, l, t]) => (
                <div key={k}>
                  <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>{l}</label>
                  <input type={t} value={form[k] ?? ''}
                    onChange={e => setForm(f => ({ ...f, [k]: t === 'number' ? parseFloat(e.target.value) || 0 : e.target.value }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                      bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              ))}
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>Status</label>
                <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
                  {['unpaid','paid','partial','cancelled'].map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="col-span-2">
                <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>Payment Method</label>
                <input value={form.payment_method || ''} onChange={e => setForm(f => ({ ...f, payment_method: e.target.value }))}
                  placeholder="bKash, Cash, Bank Transfer…"
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
            </div>
            {error && <p className="px-6 text-red-500 text-sm">{error}</p>}
            <div className="flex justify-end gap-3 px-6 py-4 border-t" style={{ borderColor: 'var(--border)' }}>
              <button onClick={() => setModal(null)} className="px-4 py-2 rounded-lg text-sm border"
                style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>Cancel</button>
              <button onClick={save} disabled={saving}
                className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold disabled:opacity-60">
                {saving ? 'Saving…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
