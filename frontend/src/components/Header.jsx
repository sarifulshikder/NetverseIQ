import React from 'react'
import { Sun, Moon, LogOut, Menu } from 'lucide-react'
import useThemeStore from '../store/themeStore.js'
import useAuthStore from '../store/authStore.js'

export default function Header({ title, onMenuClick }) {
  const { isDark, toggle } = useThemeStore()
  const logout = useAuthStore(s => s.logout)
  return (
    <header className="h-14 flex items-center justify-between px-4 border-b sticky top-0 z-10 backdrop-blur-sm"
      style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
      <div className="flex items-center gap-3">
        <button onClick={onMenuClick}
          className="lg:hidden w-9 h-9 rounded-lg flex items-center justify-center hover:bg-gray-100 dark:hover:bg-white/10">
          <Menu size={20} style={{ color: 'var(--text-secondary)' }} />
        </button>
        <h1 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>{title}</h1>
      </div>
      <div className="flex items-center gap-2">
        <button onClick={toggle} className="w-9 h-9 rounded-lg flex items-center justify-center hover:bg-gray-100 dark:hover:bg-white/10">
          {isDark ? <Sun size={18} className="text-yellow-400" /> : <Moon size={18} style={{ color: 'var(--text-secondary)' }} />}
        </button>
        <button onClick={logout} className="w-9 h-9 rounded-lg flex items-center justify-center hover:bg-red-50 dark:hover:bg-red-500/10">
          <LogOut size={18} className="text-red-400" />
        </button>
      </div>
    </header>
  )
}
