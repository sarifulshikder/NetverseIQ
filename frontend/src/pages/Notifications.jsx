import React, { useEffect, useState, useCallback } from 'react'
import { Bell, Send, RefreshCw, CheckCheck } from 'lucide-react'
import api from '../api/client.js'
import clsx from 'clsx'

const CHANNEL_STYLE = {
  email: 'bg-blue-50 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400',
  sms:   'bg-green-50 dark:bg-green-500/20 text-green-600 dark:text-green-400',
  push:  'bg-purple-50 dark:bg-purple-500/20 text-purple-600 dark:text-purple-400',
}

const EMPTY_FORM = { recipient: '', channel: 'email', subject: '', message: '' }

export default function Notifications() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [sending, setSending] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const r = await api.get('/p/notification/?limit=100')
      setNotifications(r.data.items || [])
    } catch { setNotifications([]) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const send = async () => {
    setSending(true)
    try {
      await api.post('/p/notification/send', form)
      setModal(false); setForm(EMPTY_FORM); load()
    } finally { setSending(false) }
  }

  const markRead = async (id) => {
    await api.patch(`/p/notification/${id}/read`)
    load()
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button onClick={() => setModal(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium">
          <Send size={14} /> Send Notification
        </button>
      </div>

      <div className="rounded-xl overflow-hidden shadow-sm"
        style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}>
        <div className="px-5 py-3 border-b" style={{ borderColor: 'var(--border)' }}>
          <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
            Recent Notifications
          </h3>
        </div>
        {loading ? (
          <div className="p-8 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>Loading…</div>
        ) : notifications.length === 0 ? (
          <div className="p-12 text-center">
            <Bell size={36} className="mx-auto mb-3 text-gray-300" />
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>No notifications yet</p>
          </div>
        ) : (
          <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
            {notifications.map(n => (
              <div key={n.id} className={clsx(
                'flex items-start gap-4 px-5 py-4 hover:bg-gray-50 dark:hover:bg-white/3',
                !n.is_read && 'bg-indigo-50/50 dark:bg-indigo-500/5'
              )}>
                <div className="mt-0.5">
                  <Bell size={16} className={n.is_read ? 'text-gray-300' : 'text-indigo-500'} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>{n.recipient}</span>
                    <span className={clsx('px-2 py-0.5 rounded-full text-xs', CHANNEL_STYLE[n.channel] || CHANNEL_STYLE.email)}>
                      {n.channel}
                    </span>
                    {n.status === 'sent' && <span className="text-green-500 text-xs">✓ Sent</span>}
                  </div>
                  {n.subject && <p className="text-sm font-medium mt-0.5" style={{ color: 'var(--text-primary)' }}>{n.subject}</p>}
                  <p className="text-sm mt-0.5 line-clamp-2" style={{ color: 'var(--text-secondary)' }}>{n.message}</p>
                </div>
                {!n.is_read && (
                  <button onClick={() => markRead(n.id)}
                    className="shrink-0 p-1.5 rounded hover:bg-indigo-50 dark:hover:bg-indigo-500/10 text-indigo-400" title="Mark as read">
                    <CheckCheck size={14} />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl shadow-2xl" style={{ background: 'var(--bg-secondary)' }}>
            <div className="flex items-center justify-between px-6 py-4 border-b" style={{ borderColor: 'var(--border)' }}>
              <h2 className="font-bold" style={{ color: 'var(--text-primary)' }}>Send Notification</h2>
              <button onClick={() => setModal(false)} className="text-gray-400 text-2xl leading-none">×</button>
            </div>
            <div className="p-6 space-y-4">
              {[['recipient','Recipient (email/phone)','text'],['subject','Subject','text']].map(([k,l,t]) => (
                <div key={k}>
                  <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>{l}</label>
                  <input type={t} value={form[k]}
                    onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))}
                    className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                      bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              ))}
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>Channel</label>
                <select value={form.channel} onChange={e => setForm(f => ({ ...f, channel: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
                  {['email','sms','push'].map(c => <option key={c} value={c}>{c.toUpperCase()}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>Message</label>
                <textarea value={form.message} rows={4}
                  onChange={e => setForm(f => ({ ...f, message: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2 focus:ring-indigo-500 resize-none
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t" style={{ borderColor: 'var(--border)' }}>
              <button onClick={() => setModal(false)} className="px-4 py-2 rounded-lg text-sm border"
                style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>Cancel</button>
              <button onClick={send} disabled={sending || !form.recipient || !form.message}
                className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold disabled:opacity-60">
                {sending ? 'Sending…' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
