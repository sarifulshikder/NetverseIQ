import React, { useEffect, useState, useCallback } from 'react'
import { BarChart2, Search, RefreshCw, Trash2, Plus, Wallet, TrendingDown, PieChart, Calendar } from 'lucide-react'
import api from '../api/client.js'
import clsx from 'clsx'

const CATEGORIES = ['Rent', 'Salary', 'Bandwidth', 'Electricity', 'Internet', 'Marketing', 'Office Supply', 'Others']

const EMPTY_FORM = {
  title: '', category: 'Rent', amount: 0, 
  date: new Date().toISOString().split('T')[0],
  payment_method: 'Cash', reference: '', description: ''
}

export default function Expenses() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [stats, setStats] = useState({ total_expense: 0, by_category: {} })
  const [billingStats, setBillingStats] = useState({ total_revenue: 0 })

  const loadAll = async () => {
    setLoading(true)
    try {
      const [expRes, statsRes, billRes] = await Promise.all([
        api.get('/p/expense/list?limit=100'),
        api.get('/p/expense/stats'),
        api.get('/p/billing/stats').catch(() => ({ data: { total_revenue: 0 } }))
      ])
      setItems(expRes.data.items || [])
      setTotal(expRes.data.total || 0)
      setStats(statsRes.data)
      setBillingStats(billRes.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadAll() }, [])

  const save = async () => {
    setSaving(true); setError('')
    try {
      await api.post('/p/expense/add', form)
      setModal(false); loadAll()
    } catch (e) {
      setError(e.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const del = async (id) => {
    if (!confirm('Delete this expense record?')) return
    await api.delete(`/p/expense/${id}`)
    loadAll()
  }

  const netProfit = billingStats.total_revenue - stats.total_expense

  return (
    <div className="space-y-6">
      {/* Financial Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl shadow-sm border border-green-100 bg-green-50/30 dark:bg-green-500/5 dark:border-green-500/20">
          <p className="text-xs font-bold uppercase tracking-wider text-green-600 dark:text-green-400">Total Revenue</p>
          <p className="text-3xl font-black mt-1 text-green-700 dark:text-green-300">৳{billingStats.total_revenue}</p>
        </div>
        <div className="p-5 rounded-2xl shadow-sm border border-red-100 bg-red-50/30 dark:bg-red-500/5 dark:border-red-500/20">
          <p className="text-xs font-bold uppercase tracking-wider text-red-600 dark:text-red-400">Total Expenses</p>
          <p className="text-3xl font-black mt-1 text-red-700 dark:text-red-300">৳{stats.total_expense}</p>
        </div>
        <div className={clsx(
          "p-5 rounded-2xl shadow-sm border",
          netProfit >= 0 
            ? "border-indigo-100 bg-indigo-50/30 dark:bg-indigo-500/5 dark:border-indigo-500/20" 
            : "border-orange-100 bg-orange-50/30 dark:bg-orange-500/5 dark:border-orange-500/20"
        )}>
          <p className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">Net Profit</p>
          <p className={clsx("text-3xl font-black mt-1", netProfit >= 0 ? "text-indigo-700 dark:text-indigo-300" : "text-orange-600")}>
            ৳{netProfit}
          </p>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>Expense History</h2>
        <div className="flex gap-2">
          <button onClick={loadAll} className="p-2 rounded-lg border hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
            style={{ borderColor: 'var(--border)' }}>
            <RefreshCw size={16} className={clsx('text-gray-400', loading && 'animate-spin')} />
          </button>
          <button onClick={() => { setForm(EMPTY_FORM); setModal(true) }}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold transition-all">
            <Plus size={16} /> Add Expense
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl overflow-hidden shadow-sm border"
        style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50/50 dark:bg-white/2" style={{ borderColor: 'var(--border)' }}>
                {['Date', 'Expense Title', 'Category', 'Amount', 'Method', 'Actions'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="px-4 py-12 text-center text-gray-400 animate-pulse">Loading financial records…</td></tr>
              ) : items.length === 0 ? (
                <tr><td colSpan={6} className="px-4 py-12 text-center text-gray-400">No expense records found.</td></tr>
              ) : items.map(item => (
                <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50 dark:hover:bg-white/3 transition-colors"
                  style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-4 text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
                    {new Date(item.date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-4">
                    <div className="font-bold" style={{ color: 'var(--text-primary)' }}>{item.title}</div>
                    <div className="text-[10px] text-gray-400 truncate max-w-[200px]">{item.description || 'No description'}</div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="px-2 py-1 rounded bg-indigo-50 dark:bg-indigo-500/10 text-indigo-500 text-[10px] font-bold uppercase tracking-tight">
                      {item.category}
                    </span>
                  </td>
                  <td className="px-4 py-4 font-black text-red-500">
                    ৳{item.amount}
                  </td>
                  <td className="px-4 py-4 text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
                    {item.payment_method}
                  </td>
                  <td className="px-4 py-4 text-right">
                    <button onClick={() => del(item.id)} className="p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-500/10 text-red-400 transition-colors">
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden"
            style={{ background: 'var(--bg-secondary)' }}>
            <div className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: 'var(--border)' }}>
              <h2 className="font-black text-xl" style={{ color: 'var(--text-primary)' }}>Add New Expense</h2>
              <button onClick={() => setModal(false)} className="text-gray-400 hover:text-gray-600 text-3xl leading-none">×</button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Expense Title</label>
                <input value={form.title} required placeholder="e.g. June Office Rent"
                  onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                  className="mt-1 w-full px-4 py-3 rounded-xl border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Category</label>
                  <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                    className="mt-1 w-full px-4 py-3 rounded-xl border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                    {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Amount (৳)</label>
                  <input type="number" value={form.amount} required
                    onChange={e => setForm(f => ({ ...f, amount: parseFloat(e.target.value) || 0 }))}
                    className="mt-1 w-full px-4 py-3 rounded-xl border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                      bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Date</label>
                  <input type="date" value={form.date}
                    onChange={e => setForm(f => ({ ...f, date: e.target.value }))}
                    className="mt-1 w-full px-4 py-3 rounded-xl border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Payment Method</label>
                  <select value={form.payment_method} onChange={e => setForm(f => ({ ...f, payment_method: e.target.value }))}
                    className="mt-1 w-full px-4 py-3 rounded-xl border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                    {['Cash','Bank','BKash','Nagad'].map(m => <option key={m} value={m}>{m}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Description / Reference</label>
                <textarea value={form.description} rows={2}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  className="mt-1 w-full px-4 py-3 rounded-xl border text-sm outline-none resize-none
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100" />
              </div>
            </div>
            {error && <p className="px-6 pb-4 text-red-500 text-xs font-bold">{error}</p>}
            <div className="flex justify-end gap-3 px-6 py-5 border-t bg-gray-50 dark:bg-gray-900/50" style={{ borderColor: 'var(--border)' }}>
              <button onClick={() => setModal(false)} className="px-6 py-2.5 rounded-xl text-sm font-bold border hover:bg-white dark:hover:bg-white/5 transition-colors"
                style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>Cancel</button>
              <button onClick={save} disabled={saving}
                className="px-8 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-black shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-60">
                {saving ? 'Processing…' : 'Record Expense'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
