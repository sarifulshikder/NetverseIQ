import React, { useEffect, useState, useCallback } from 'react'
import { Zap, Search, RefreshCw, Trash2, Edit2, Plus, Box, Truck, AlertTriangle, DollarSign } from 'lucide-react'
import api from '../api/client.js'
import clsx from 'clsx'

const STATUS_STYLES = {
  in_stock: 'bg-green-50 dark:bg-green-500/20 text-green-600 dark:text-green-400',
  deployed: 'bg-blue-50 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400',
  faulty:   'bg-red-50 dark:bg-red-500/20 text-red-600 dark:text-red-400',
  lost:     'bg-gray-100 dark:bg-white/10 text-gray-500',
}

const EMPTY_FORM = {
  name: '', category: 'ONU', serial_number: '', mac_address: '',
  status: 'in_stock', customer_id: '', customer_name: '',
  location: '', purchase_price: 0, supplier: '', notes: ''
}

export default function Inventory() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState(null) // null | 'add' | {item}
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [stats, setStats] = useState({ total_items: 0, in_stock: 0, deployed: 0, stock_value: 0 })

  const loadStats = async () => {
    try {
      const r = await api.get('/p/inventory/stats')
      setStats(r.data)
    } catch {}
  }

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const r = await api.get(`/p/inventory/items?limit=100&search=${encodeURIComponent(search)}`)
      setItems(r.data.items || [])
      setTotal(r.data.total || 0)
    } catch {
      setItems([])
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => { load(); loadStats() }, [load])

  const openAdd = () => { setForm(EMPTY_FORM); setError(''); setModal('add') }
  const openEdit = (item) => { setForm({ ...item }); setError(''); setModal(item) }

  const save = async () => {
    setSaving(true); setError('')
    try {
      if (modal === 'add') {
        await api.post('/p/inventory/items', form)
      } else {
        await api.put(`/p/inventory/items/${modal.id}`, form)
      }
      setModal(null); load(); loadStats()
    } catch (e) {
      setError(e.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const del = async (id) => {
    if (!confirm('Delete this item from inventory?')) return
    await api.delete(`/p/inventory/items/${id}`)
    load(); loadStats()
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Assets', value: stats.total_items, icon: Box, color: 'text-indigo-600' },
          { label: 'In Stock', value: stats.in_stock, icon: Truck, color: 'text-green-600' },
          { label: 'Deployed', value: stats.deployed, icon: Zap, color: 'text-blue-600' },
          { label: 'Stock Value', value: `৳${stats.stock_value}`, icon: DollarSign, color: 'text-yellow-600' },
        ].map((s, i) => (
          <div key={i} className="p-4 rounded-xl shadow-sm border" style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>{s.label}</p>
                <p className="text-xl font-bold mt-1" style={{ color: 'var(--text-primary)' }}>{s.value}</p>
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
            value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search by name, serial, or customer…"
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
          <Plus size={15} /> Add Item
        </button>
      </div>

      {/* Table */}
      <div className="rounded-xl overflow-hidden shadow-sm border"
        style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b" style={{ borderColor: 'var(--border)' }}>
                {['Item Info', 'Serial/MAC', 'Status', 'Deployed To', 'Price', 'Actions'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>Loading…</td></tr>
              ) : items.length === 0 ? (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>No items found</td></tr>
              ) : items.map(item => (
                <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50 dark:hover:bg-white/3 transition-colors"
                  style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-3">
                    <div className="font-medium" style={{ color: 'var(--text-primary)' }}>{item.name}</div>
                    <div className="text-[10px] text-gray-400 uppercase font-semibold tracking-tight">{item.category}</div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="text-xs font-mono" style={{ color: 'var(--text-primary)' }}>{item.serial_number}</div>
                    <div className="text-[10px] text-gray-400 font-mono">{item.mac_address || '—'}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={clsx('px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider', STATUS_STYLES[item.status])}>
                      {item.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {item.customer_name ? (
                      <div>
                        <div className="text-xs font-medium text-indigo-500">{item.customer_name}</div>
                        <div className="text-[10px] text-gray-400">ID: {item.customer_id}</div>
                      </div>
                    ) : <span className="text-gray-400 italic text-xs">Unassigned</span>}
                  </td>
                  <td className="px-4 py-3 font-semibold" style={{ color: 'var(--text-primary)' }}>
                    ৳{item.purchase_price}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center gap-1 justify-end">
                      <button onClick={() => openEdit(item)} className="p-1.5 rounded hover:bg-indigo-50 dark:hover:bg-indigo-500/10 text-indigo-500 transition-colors">
                        <Edit2 size={13} />
                      </button>
                      <button onClick={() => del(item.id)} className="p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-500/10 text-red-400 transition-colors">
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
          <div className="w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden"
            style={{ background: 'var(--bg-secondary)' }}>
            <div className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: 'var(--border)' }}>
              <h2 className="font-bold" style={{ color: 'var(--text-primary)' }}>
                {modal === 'add' ? 'Add Inventory Item' : 'Edit Item'}
              </h2>
              <button onClick={() => setModal(null)} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">×</button>
            </div>
            <div className="p-6 grid grid-cols-2 gap-4 max-h-[70vh] overflow-y-auto">
              <div className="col-span-2 md:col-span-1">
                <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Item Name</label>
                <input value={form.name} required
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div className="col-span-2 md:col-span-1">
                <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Category</label>
                <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                  {['ONU','Router','Cable','Splitter','SFP','Other'].map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Serial Number</label>
                <input value={form.serial_number} required
                  onChange={e => setForm(f => ({ ...f, serial_number: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">MAC Address</label>
                <input value={form.mac_address}
                  onChange={e => setForm(f => ({ ...f, mac_address: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Status</label>
                <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                  {['in_stock','deployed','faulty','lost'].map(s => <option key={s} value={s}>{s.replace('_',' ')}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Purchase Price (৳)</label>
                <input type="number" value={form.purchase_price}
                  onChange={e => setForm(f => ({ ...f, purchase_price: parseFloat(e.target.value) || 0 }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>

              <div className="col-span-2 border-t pt-4 mt-2">
                <p className="text-xs font-bold uppercase text-indigo-500 mb-3">Deployment Details (Optional)</p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Customer ID</label>
                    <input type="number" value={form.customer_id || ''}
                      onChange={e => setForm(f => ({ ...f, customer_id: parseInt(e.target.value) || '' }))}
                      className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none
                        bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Customer Name</label>
                    <input value={form.customer_name || ''}
                      onChange={e => setForm(f => ({ ...f, customer_name: e.target.value }))}
                      className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none
                        bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                    />
                  </div>
                </div>
              </div>

              <div className="col-span-2">
                <label className="text-xs font-semibold uppercase tracking-wide text-gray-400">Supplier / Notes</label>
                <textarea value={form.notes || ''} rows={2}
                  onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none resize-none
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100" />
              </div>
            </div>
            {error && <p className="px-6 pb-4 text-red-500 text-xs font-medium">{error}</p>}
            <div className="flex justify-end gap-3 px-6 py-4 border-t bg-gray-50 dark:bg-gray-900/50" style={{ borderColor: 'var(--border)' }}>
              <button onClick={() => setModal(null)} className="px-4 py-2 rounded-lg text-sm border hover:bg-white dark:hover:bg-white/5 transition-colors"
                style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>Cancel</button>
              <button onClick={save} disabled={saving}
                className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold transition-colors disabled:opacity-60">
                {saving ? 'Saving…' : 'Save Item'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
