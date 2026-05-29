import React, { useEffect, useState } from 'react'
import { Zap, Plus, Edit2, Trash2, RefreshCw, Check, X } from 'lucide-react'
import api from '../api/client.js'
import clsx from 'clsx'

const EMPTY_FORM = {
  name: '', speed_mbps: 5, price: 500, 
  description: '', is_active: true,
  upload_limit: '5M', download_limit: '5M'
}

export default function Packages() {
  const [packages, setPackages] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null) // null | 'add' | {package}
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const r = await api.get('/p/packages/list')
      setPackages(r.data || [])
    } catch {
      setPackages([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openAdd = () => { setForm(EMPTY_FORM); setError(''); setModal('add') }
  const openEdit = (p) => { setForm({ ...p }); setError(''); setModal(p) }

  const save = async () => {
    setSaving(true); setError('')
    try {
      if (modal === 'add') {
        await api.post('/p/packages/add', form)
      } else {
        await api.put(`/p/packages/${modal.id}`, form)
      }
      setModal(null); load()
    } catch (e) {
      setError(e.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const del = async (id) => {
    if (!confirm('Delete this package? This might affect billing.')) return
    await api.delete(`/p/packages/${id}`)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-black" style={{ color: 'var(--text-primary)' }}>Service Packages</h2>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Define your internet plans and pricing</p>
        </div>
        <button onClick={openAdd}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold shadow-lg shadow-indigo-600/20 transition-all">
          <Plus size={18} /> Create Package
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {loading ? (
          [1,2,3].map(i => <div key={i} className="h-48 rounded-2xl animate-pulse bg-gray-100 dark:bg-white/5" />)
        ) : packages.length === 0 ? (
          <div className="col-span-full p-12 text-center border-2 border-dashed rounded-2xl border-gray-200 dark:border-white/10">
            <Zap size={40} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-400">No packages defined yet.</p>
          </div>
        ) : packages.map(pkg => (
          <div key={pkg.id} 
            className="group relative p-6 rounded-2xl border transition-all hover:shadow-xl hover:-translate-y-1"
            style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
            
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                <Zap size={24} fill="currentColor" />
              </div>
              <div className="flex gap-1">
                <button onClick={() => openEdit(pkg)} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-white/5 text-gray-400 hover:text-indigo-500 transition-colors">
                  <Edit2 size={14} />
                </button>
                <button onClick={() => del(pkg.id)} className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 text-gray-400 hover:text-red-500 transition-colors">
                  <Trash2 size={14} />
                </button>
              </div>
            </div>

            <h3 className="text-lg font-black" style={{ color: 'var(--text-primary)' }}>{pkg.name}</h3>
            <p className="text-xs mb-4" style={{ color: 'var(--text-secondary)' }}>{pkg.description || 'No description provided'}</p>
            
            <div className="flex items-baseline gap-1 mb-4">
              <span className="text-3xl font-black text-indigo-600">৳{pkg.price}</span>
              <span className="text-xs font-bold text-gray-400 uppercase">/ month</span>
            </div>

            <div className="flex items-center gap-4 pt-4 border-t border-dashed border-gray-100 dark:border-white/5">
              <div className="flex-1">
                <p className="text-[10px] font-bold uppercase text-gray-400">Speed</p>
                <p className="text-sm font-black text-gray-700 dark:text-gray-200">{pkg.speed_mbps} Mbps</p>
              </div>
              <div className="flex-1 text-right">
                <p className="text-[10px] font-bold uppercase text-gray-400">Status</p>
                <span className={clsx(
                  "text-[10px] font-black uppercase tracking-widest",
                  pkg.is_active ? "text-green-500" : "text-red-500"
                )}>
                  {pkg.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {modal !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-3xl shadow-2xl overflow-hidden"
            style={{ background: 'var(--bg-secondary)' }}>
            <div className="px-8 py-6 border-b flex items-center justify-between" style={{ borderColor: 'var(--border)' }}>
              <h2 className="text-xl font-black" style={{ color: 'var(--text-primary)' }}>
                {modal === 'add' ? 'Create New Plan' : 'Update Plan'}
              </h2>
              <button onClick={() => setModal(null)} className="text-gray-400 hover:text-gray-600 text-3xl leading-none">×</button>
            </div>
            <div className="p-8 space-y-5">
              <div>
                <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1 block">Package Name</label>
                <input value={form.name} required placeholder="e.g. Home Basic 5M"
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1 block">Speed (Mbps)</label>
                  <input type="number" value={form.speed_mbps} required
                    onChange={e => setForm(f => ({ ...f, speed_mbps: parseInt(e.target.value) || 0 }))}
                    className="w-full px-4 py-3 rounded-xl border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1 block">Monthly Price (৳)</label>
                  <input type="number" value={form.price} required
                    onChange={e => setForm(f => ({ ...f, price: parseFloat(e.target.value) || 0 }))}
                    className="w-full px-4 py-3 rounded-xl border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1 block">Upload Limit</label>
                  <input value={form.upload_limit} placeholder="e.g. 5M"
                    onChange={e => setForm(f => ({ ...f, upload_limit: e.target.value }))}
                    className="w-full px-4 py-3 rounded-xl border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1 block">Download Limit</label>
                  <input value={form.download_limit} placeholder="e.g. 5M"
                    onChange={e => setForm(f => ({ ...f, download_limit: e.target.value }))}
                    className="w-full px-4 py-3 rounded-xl border text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                  />
                </div>
              </div>
              <div>
                <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1 block">Description</label>
                <textarea value={form.description} rows={2}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl border text-sm outline-none resize-none
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100" />
              </div>
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" checked={form.is_active}
                  onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))}
                  className="w-5 h-5 accent-indigo-600 rounded-lg"
                />
                <span className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>Is Active / Selling</span>
              </label>
            </div>
            {error && <p className="px-8 pb-4 text-red-500 text-xs font-bold">{error}</p>}
            <div className="flex justify-end gap-3 px-8 py-6 border-t bg-gray-50/50 dark:bg-white/2" style={{ borderColor: 'var(--border)' }}>
              <button onClick={() => setModal(null)} className="px-6 py-3 rounded-xl text-sm font-black border transition-colors hover:bg-white dark:hover:bg-white/5"
                style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>Cancel</button>
              <button onClick={save} disabled={saving}
                className="px-8 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-black shadow-xl shadow-indigo-600/30 transition-all disabled:opacity-60">
                {saving ? 'Processing…' : 'Save Package'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
