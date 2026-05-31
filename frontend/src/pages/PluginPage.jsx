import React, { useEffect, useState, useCallback } from 'react'
import { RefreshCw, PlusCircle, Trash2, Edit2 } from 'lucide-react'
import api from '../api/client.js'

export default function PluginPage({ pluginId, apiPrefix, title, listEndpoint, fields: manifestFields }) {
  const [items, setItems]     = useState([])
  const [total, setTotal]     = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')
  const [modal, setModal]     = useState(null)
  const [form, setForm]       = useState({})
  const [saving, setSaving]   = useState(false)
  const [keys, setKeys]       = useState(manifestFields || [])

  const base = apiPrefix?.replace(/^\/api/, '') || `/p/${pluginId}`
  const listPath = listEndpoint
    ? listEndpoint.replace(/^\/api/, '')
    : `${base}/list`

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const r = await api.get(listPath)
      const data = r.data
      let arr = []
      if (Array.isArray(data)) {
        arr = data
      } else if (data && typeof data === 'object') {
        const listKey = Object.keys(data).find(k => Array.isArray(data[k]))
        arr = listKey ? data[listKey] : []
      }
      setItems(arr)
      setTotal(data?.total ?? arr.length)
      // data থাকলে data থেকে keys নাও, না থাকলে manifest fields ব্যবহার করো
      if (arr.length > 0) {
        setKeys(Object.keys(arr[0]).filter(k =>
          !['id','created_at','updated_at','sa_instance_state','password','hashed_password'].includes(k)
        ).slice(0, 6))
      } else if (manifestFields?.length > 0) {
        setKeys(manifestFields)
      }
    } catch (e) {
      setError(e.response?.data?.detail || `Failed to load data`)
      if (manifestFields?.length > 0) setKeys(manifestFields)
    } finally { setLoading(false) }
  }, [listPath])

  useEffect(() => { load() }, [load])

  const openAdd  = () => { 
    const emptyForm = {}
    keys.forEach(k => emptyForm[k] = '')
    setForm(emptyForm)
    setModal('add') 
  }
  const openEdit = (item) => { setForm({ ...item }); setModal(item) }

  const save = async () => {
    setSaving(true)
    try {
      if (modal === 'add') await api.post(`${base}/`, form)
      else await api.put(`${base}/${modal.id}`, form)
      setModal(null); load()
    } catch (e) {
      alert(e.response?.data?.detail || 'Save failed')
    } finally { setSaving(false) }
  }

  const del = async (id) => {
    if (!confirm('Delete this item?')) return
    try {
      await api.delete(`${base}/${id}`)
      load()
    } catch (e) {
      alert(e.response?.data?.detail || 'Delete failed')
    }
  }

  const fmt = (v) => {
    if (v === null || v === undefined) return '—'
    if (typeof v === 'boolean') return v ? '✓' : '✗'
    if (typeof v === 'string' && v.match(/^\d{4}-\d{2}-\d{2}T/))
      return new Date(v).toLocaleDateString()
    if (typeof v === 'object') return JSON.stringify(v).slice(0, 50)
    return String(v).slice(0, 80)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <button onClick={load}
          className="p-2 rounded-lg border hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
          style={{ borderColor: 'var(--border)' }}>
          <RefreshCw size={15} className={`text-gray-400 ${loading ? 'animate-spin' : ''}`} />
        </button>
        <button onClick={openAdd}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium transition-colors">
          <PlusCircle size={15} /> Add New
        </button>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-lg bg-red-50 dark:bg-red-500/10 text-red-500 text-sm">{error}</div>
      )}

      <div className="rounded-xl overflow-hidden shadow-sm"
        style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}>
        <div className="px-5 py-3 border-b" style={{ borderColor: 'var(--border)' }}>
          <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
            {title} <span className="text-gray-400 font-normal">({total})</span>
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b" style={{ borderColor: 'var(--border)' }}>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                  style={{ color: 'var(--text-secondary)' }}>ID</th>
                {keys.map(k => (
                  <th key={k} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}>
                    {k.replace(/_/g, ' ')}
                  </th>
                ))}
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                  style={{ color: 'var(--text-secondary)' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={keys.length + 2} className="px-4 py-8 text-center text-sm"
                  style={{ color: 'var(--text-secondary)' }}>Loading…</td></tr>
              ) : items.length === 0 ? (
                <tr><td colSpan={keys.length + 2} className="px-4 py-8 text-center text-sm"
                  style={{ color: 'var(--text-secondary)' }}>No data found</td></tr>
              ) : items.map((item, idx) => (
                <tr key={item.id ?? idx} className="border-b last:border-0 hover:bg-gray-50 dark:hover:bg-white/3 transition-colors"
                  style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-3 text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>{item.id ?? idx+1}</td>
                  {keys.map(k => (
                    <td key={k} className="px-4 py-3 text-xs max-w-xs truncate"
                      style={{ color: 'var(--text-secondary)' }}>{fmt(item[k])}</td>
                  ))}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button onClick={() => openEdit(item)}
                        className="p-1.5 rounded hover:bg-indigo-50 dark:hover:bg-indigo-500/10 text-indigo-500 transition-colors">
                        <Edit2 size={13} />
                      </button>
                      {item.id && (
                        <button onClick={() => del(item.id)}
                          className="p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-500/10 text-red-400 transition-colors">
                          <Trash2 size={13} />
                        </button>
                      )}
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
          <div className="w-full max-w-lg rounded-2xl shadow-2xl overflow-y-auto max-h-[90vh]"
            style={{ background: 'var(--bg-secondary)' }}>
            <div className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: 'var(--border)' }}>
              <h2 className="font-bold" style={{ color: 'var(--text-primary)' }}>
                {modal === 'add' ? 'Add New' : 'Edit Item'}
              </h2>
              <button onClick={() => setModal(null)} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">×</button>
            </div>
            <div className="p-6 grid grid-cols-2 gap-4">
              {Object.keys(form).filter(k => !['id','created_at','updated_at'].includes(k)).map(k => (
                <div key={k} className="col-span-2 sm:col-span-1">
                  <label className="text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}>{k.replace(/_/g, ' ')}</label>
                  <input
                    value={form[k] ?? ''}
                    onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                      bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              ))}
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t" style={{ borderColor: 'var(--border)' }}>
              <button onClick={() => setModal(null)}
                className="px-4 py-2 rounded-lg text-sm border transition-colors hover:bg-gray-50 dark:hover:bg-white/5"
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
