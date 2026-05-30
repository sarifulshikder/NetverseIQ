import React, { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar.jsx'
import Header from './Header.jsx'
import useAuthStore from '../store/authStore.js'

function toTitle(pathname) {
  if (pathname === '/') return 'Dashboard'
  const segment = pathname.split('/').filter(Boolean).pop() || ''
  return segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ')
}

export default function Layout() {
  const user = useAuthStore(s => s.user)
  const { pathname } = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-screen">
      <div className="hidden lg:flex lg:flex-shrink-0">
        <Sidebar user={user} />
      </div>
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 flex lg:hidden">
          <div className="fixed inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
          <div className="relative z-50">
            <Sidebar user={user} onClose={() => setSidebarOpen(false)} />
          </div>
        </div>
      )}
      <div className="flex-1 flex flex-col min-w-0">
        <Header title={toTitle(pathname)} onMenuClick={() => setSidebarOpen(o => !o)} />
        <main className="flex-1 p-3 lg:p-6 overflow-auto" style={{ background: 'var(--bg-primary)' }}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
