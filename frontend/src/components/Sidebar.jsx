import React, { useEffect, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Users, FileText, Receipt, Bell,
  BarChart2, Puzzle, Settings, ChevronRight, Wifi,
  Shield, Activity, Link
} from 'lucide-react'
import api from '../api/client.js'
import clsx from 'clsx'

// Icon map for plugin menu items
const ICONS = {
  LayoutDashboard, Users, FileText, Receipt, Bell,
  BarChart2, Puzzle, Settings, Wifi, Shield, Activity, Link,
}

const STATIC_MENU = [
  { label: 'Dashboard',  icon: 'LayoutDashboard', path: '/' },
  { label: 'Users',      icon: 'Users',           path: '/users', superonly: true },
  { label: 'Plugins',   icon: 'Puzzle',           path: '/plugins', superonly: true },
]

function NavItem({ item }) {
  const Icon = ICONS[item.icon] || Puzzle
  return (
    <NavLink
      to={item.path}
      end={item.path === '/'}
      className={({ isActive }) =>
        clsx(
          'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
          isActive
            ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30'
            : 'text-indigo-200 hover:bg-white/10 hover:text-white'
        )
      }
    >
      <Icon size={17} />
      <span>{item.label}</span>
    </NavLink>
  )
}

export default function Sidebar({ user }) {
  const [pluginMenu, setPluginMenu] = useState([])

  useEffect(() => {
    api.get('/plugins/menu')
      .then(r => {
        // Normalize paths: remove leading slash to match relative routes
        const normalized = r.data.map(item => ({
            ...item,
            path: item.path.startsWith('/') ? item.path.slice(1) : item.path
        }));
        console.log("DEBUG: Normalized plugin menu paths:", normalized);
        setPluginMenu(normalized);
      })
      .catch(() => {})
  }, [])

  const isSuper = user?.is_superuser

  return (
    <aside className="w-60 h-screen flex flex-col sticky top-0"
      style={{ background: 'var(--bg-sidebar)' }}>

      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-white/10">
        <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center">
          <Wifi size={16} className="text-white" />
        </div>
        <div>
          <span className="text-white font-bold text-base tracking-tight">NetverseIQ</span>
          <p className="text-indigo-300 text-[10px] leading-none mt-0.5">ISP Management</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto scrollbar-thin">

        <p className="text-indigo-400 text-[10px] font-semibold uppercase tracking-widest px-3 mb-2">
          Core
        </p>
        {STATIC_MENU.filter(i => !i.superonly || isSuper).map(item => (
          <NavItem key={item.path} item={item} />
        ))}

        {pluginMenu.length > 0 && (
          <>
            <p className="text-indigo-400 text-[10px] font-semibold uppercase tracking-widest px-3 mt-5 mb-2">
              Modules
            </p>
            {pluginMenu.map(item => (
              <NavItem key={item.path} item={item} />
            ))}
          </>
        )}
      </nav>

      {/* User info */}
      <div className="px-4 py-4 border-t border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-white text-sm font-semibold">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-medium truncate">{user?.name}</p>
            <p className="text-indigo-300 text-xs truncate">{user?.email}</p>
          </div>
          {user?.is_superuser && (
            <Shield size={14} className="text-brand-400 shrink-0" />
          )}
        </div>
      </div>
    </aside>
  )
}
