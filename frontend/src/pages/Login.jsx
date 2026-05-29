import React, { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { Wifi, Eye, EyeOff, Loader2 } from 'lucide-react'
import useAuthStore from '../store/authStore.js'

export default function Login() {
  const { login, isAuthenticated } = useAuthStore()
  const [email, setEmail] = useState('admin@netverseiq.local')
  const [password, setPassword] = useState('Admin@1234')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (isAuthenticated) return <Navigate to="/" replace />

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4"
      style={{ background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%)' }}>

      <div className="w-full max-w-sm">
        {/* Card */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl overflow-hidden">

          {/* Header */}
          <div className="px-8 pt-8 pb-6 text-center"
            style={{ background: 'linear-gradient(135deg, #4f46e5, #7c3aed)' }}>
            <div className="w-14 h-14 rounded-2xl bg-white/20 flex items-center justify-center mx-auto mb-3">
              <Wifi size={28} className="text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">NetverseIQ</h1>
            <p className="text-indigo-200 text-sm mt-1">ISP Management Platform</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="px-8 py-6 space-y-4">
            <div>
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                className="mt-1.5 w-full px-4 py-2.5 rounded-lg border text-sm outline-none transition-all
                  focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                  bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700
                  text-gray-900 dark:text-gray-100"
                placeholder="admin@netverseiq.local"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Password
              </label>
              <div className="relative mt-1.5">
                <input
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  className="w-full px-4 py-2.5 pr-11 rounded-lg border text-sm outline-none transition-all
                    focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                    bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700
                    text-gray-900 dark:text-gray-100"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPw(p => !p)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg px-4 py-3">
                <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold
                text-sm transition-all disabled:opacity-60 flex items-center justify-center gap-2 mt-2"
            >
              {loading && <Loader2 size={16} className="animate-spin" />}
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

          <div className="px-8 pb-6 text-center">
            <p className="text-xs text-gray-400">NetverseIQ v1.0.0 — Plug & Play ISP Platform</p>
          </div>
        </div>
      </div>
    </div>
  )
}
