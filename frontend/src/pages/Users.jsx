import React, { useEffect, useState } from 'react'
import { UserPlus, Trash2, Shield, CheckCircle, XCircle } from 'lucide-react'
import api from '../api/client.js'
import clsx from 'clsx'

const EMPTY_FORM = { name: '', email: '', password: '', is_superuser: false }

export default function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    api.get('/users/').then(r => setUsers(r.data)).finally(() => setLoading(false))
  }

  useEffect(load, [])

  const save = async () => {
    setSaving(true); setError('')
    try {
      await api.post('/users/', form)
      setModal(false); load()
    } catch (e) { setError(e.response?.data?.detail || 'Failed') }
    finally { setSaving(false) }
  }

  const del = async (id) => {
    if (!confirm('Delete user?')) return
    await api.delete(`/users/${id}`)
    load()
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button onClick={() => { setForm(EMPTY_FORM); setError(''); setModal(true) }}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium">
          <UserPlus size={15} /> Add User
        </button>
      </div>

      <div className="rounded-xl overflow-hidden shadow-sm"
        style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b" style={{ borderColor: 'var(--border)' }}>
              {['Name','Email','Superuser','Status','Actions'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                  style={{ color: 'var(--text-secondary)' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>Loading…</td></tr>
            ) : users.map(u => (
              <tr key={u.id} className="border-b last:border-0 hover:bg-gray-50 dark:hover:bg-white/3"
                style={{ borderColor: 'var(--border)' }}>
                <td className="px-4 py-3 font-medium" style={{ color: 'var(--text-primary)' }}>{u.name}</td>
                <td className="px-4 py-3 text-xs" style={{ color: 'var(--text-secondary)' }}>{u.email}</td>
                <td className="px-4 py-3">
                  {u.is_superuser
                    ? <Shield size={15} className="text-indigo-500" />
                    : <span className="text-gray-300">—</span>
                  }
                </td>
                <td className="px-4 py-3">
                  <span className={clsx('flex items-center gap-1 text-xs font-medium w-fit',
                    u.is_active ? 'text-green-500' : 'text-red-400')}>
                    {u.is_active ? <><CheckCircle size={12} /> Active</> : <><XCircle size={12} /> Inactive</>}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button onClick={() => del(u.id)} className="p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-500/10 text-red-400">
                    <Trash2 size={13} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-2xl shadow-2xl" style={{ background: 'var(--bg-secondary)' }}>
            <div className="flex items-center justify-between px-6 py-4 border-b" style={{ borderColor: 'var(--border)' }}>
              <h2 className="font-bold" style={{ color: 'var(--text-primary)' }}>Add User</h2>
              <button onClick={() => setModal(false)} className="text-gray-400 text-2xl leading-none">×</button>
            </div>
            <div className="p-6 space-y-4">
              {[['name','Name','text'],['email','Email','email'],['password','Password','password']].map(([k,l,t]) => (
                <div key={k}>
                  <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>{l}</label>
                  <input type={t} value={form[k]}
                    onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                      bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              ))}
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" checked={form.is_superuser}
                  onChange={e => setForm(f => ({ ...f, is_superuser: e.target.checked }))}
                  className="w-4 h-4 accent-indigo-600"
                />
                <span className="text-sm" style={{ color: 'var(--text-primary)' }}>Superuser (full access)</span>
              </label>
              {error && <p className="text-red-500 text-sm">{error}</p>}
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t" style={{ borderColor: 'var(--border)' }}>
              <button onClick={() => setModal(false)} className="px-4 py-2 rounded-lg text-sm border"
                style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>Cancel</button>
              <button onClick={save} disabled={saving}
                className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold disabled:opacity-60">
                {saving ? 'Creating…' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
