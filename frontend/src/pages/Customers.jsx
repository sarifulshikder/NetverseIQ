import React, { useEffect, useState, useCallback } from 'react'
import { UserPlus, Search, RefreshCw, Trash2, Edit2, CheckCircle, XCircle, Clock } from 'lucide-react'
import api from '../api/client.js'
import clsx from 'clsx'

const STATUS_STYLES = {
  active:    'bg-green-50 dark:bg-green-500/20 text-green-600 dark:text-green-400',
  suspended: 'bg-red-50 dark:bg-red-500/20 text-red-600 dark:text-red-400',
  pending:   'bg-yellow-50 dark:bg-yellow-500/20 text-yellow-600 dark:text-yellow-400',
  expired:   'bg-gray-100 dark:bg-white/10 text-gray-500',
}

const EMPTY_FORM = {
  name: '', email: '', phone: '', address: '', area_zone: '',
  connection_id: '', package_name: '', monthly_fee: 0,
  ip_address: '', mac_address: '', status: 'pending', notes: '',
}

export default function Customers() {
  const [customers, setCustomers] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState(null) // null | 'add' | {customer}
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const r = await api.get(`/p/customer/?search=${encodeURIComponent(search)}&limit=100`)
      setCustomers(r.data.items || [])
      setTotal(r.data.total || 0)
    } catch {
      setCustomers([])
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => { load() }, [load])

  const openAdd = () => { setForm(EMPTY_FORM); setError(''); setModal('add') }
  const openEdit = (c) => { setForm({ ...c }); setError(''); setModal(c) }

  const save = async () => {
    setSaving(true); setError('')
    try {
      if (modal === 'add') {
        await api.post('/p/customer/', form)
      } else {
        await api.put(`/p/customer/${modal.id}`, form)
      }
      setModal(null); load()
    } catch (e) {
      setError(e.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const del = async (id) => {
    if (!confirm('Delete this customer?')) return
    await api.delete(`/p/customer/${id}`)
    load()
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search name, email, connection ID…"
            className="w-full pl-9 pr-4 py-2 text-sm rounded-lg border outline-none focus:ring-2 focus:ring-indigo-500
              bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <button onClick={load} className="p-2 rounded-lg border hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
          style={{ borderColor: 'var(--border)' }}>
          <RefreshCw size={15} className={clsx('text-gray-400', loading && 'animate-spin')} />
        </button>
        <button onClick={openAdd}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium transition-colors">
          <UserPlus size={15} /> Add Customer
        </button>
      </div>

      {/* Table */}
      <div className="rounded-xl overflow-hidden shadow-sm"
        style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}>
        <div className="px-5 py-3 border-b flex items-center justify-between"
          style={{ borderColor: 'var(--border)' }}>
          <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
            Customers <span className="text-gray-400 font-normal">({total})</span>
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b" style={{ borderColor: 'var(--border)' }}>
                {['Name', 'Connection ID', 'Package', 'Fee', 'Status', 'Actions'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>Loading…</td></tr>
              ) : customers.length === 0 ? (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>No customers found</td></tr>
              ) : customers.map(c => (
                <tr key={c.id} className="border-b last:border-0 hover:bg-gray-50 dark:hover:bg-white/3 transition-colors"
                  style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-3">
                    <div className="font-medium" style={{ color: 'var(--text-primary)' }}>{c.name}</div>
                    <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>{c.email}</div>
                  </td>
                  <td className="px-4 py-3 text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
                    {c.connection_id || '—'}
                  </td>
                  <td className="px-4 py-3 text-xs" style={{ color: 'var(--text-secondary)' }}>
                    {c.package_name || '—'}
                  </td>
                  <td className="px-4 py-3 text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {c.monthly_fee ? `৳${c.monthly_fee}` : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={clsx('px-2 py-0.5 rounded-full text-xs font-medium', STATUS_STYLES[c.status] || STATUS_STYLES.pending)}>
                      {c.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button onClick={() => openEdit(c)} className="p-1.5 rounded hover:bg-indigo-50 dark:hover:bg-indigo-500/10 text-indigo-500 transition-colors">
                        <Edit2 size={13} />
                      </button>
                      <button onClick={() => del(c.id)} className="p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-500/10 text-red-400 transition-colors">
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

      {/* Modal */}
      {modal !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl shadow-2xl overflow-y-auto max-h-[90vh]"
            style={{ background: 'var(--bg-secondary)' }}>
            <div className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: 'var(--border)' }}>
              <h2 className="font-bold" style={{ color: 'var(--text-primary)' }}>
                {modal === 'add' ? 'Add Customer' : 'Edit Customer'}
              </h2>
              <button onClick={() => setModal(null)} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">×</button>
            </div>
            <div className="p-6 grid grid-cols-2 gap-4">
              {[
                ['name','Name','text',true], ['email','Email','email',true],
                ['phone','Phone','text'], ['connection_id','Connection ID','text'],
                ['package_name','Package','text'], ['monthly_fee','Monthly Fee (৳)','number'],
                ['ip_address','IP Address','text'], ['mac_address','MAC Address','text'],
                ['area_zone','Area/Zone','text'],
              ].map(([key, label, type, req]) => (
                <div key={key} className={key === 'name' || key === 'email' || key === 'area_zone' ? 'col-span-2' : ''}>
                  <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>{label}</label>
                  <input type={type || 'text'} value={form[key] ?? ''} required={req}
                    onChange={e => setForm(f => ({ ...f, [key]: type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                      bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              ))}
              <div className="col-span-2">
                <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>Status</label>
                <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
                  {['pending','active','suspended','expired'].map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="col-span-2">
                <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>Notes</label>
                <textarea value={form.notes} rows={2} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500 resize-none
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100" />
              </div>
            </div>
            {error && <p className="px-6 text-red-500 text-sm">{error}</p>}
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
