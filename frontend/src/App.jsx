import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import useAuthStore from './store/authStore.js'
import useThemeStore from './store/themeStore.js'
import Layout from './components/Layout.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Plugins from './pages/Plugins.jsx'
import Customers from './pages/Customers.jsx'
import Billing from './pages/Billing.jsx'
import Notifications from './pages/Notifications.jsx'
import Users from './pages/Users.jsx'
import Support from './pages/Support.jsx'
import Inventory from './pages/Inventory.jsx'
import Expenses from './pages/Expenses.jsx'
import Packages from './pages/Packages.jsx'
import Subscriptions from './pages/Subscriptions.jsx'

function PrivateRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuthStore()
  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--bg-primary)' }}>
      <div className="flex flex-col items-center gap-3">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Loading NetverseIQ…</p>
      </div>
    </div>
  )
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

export default function App() {
  const { init } = useAuthStore()
  const { init: initTheme } = useThemeStore()

  useEffect(() => {
    initTheme()
    init()
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="plugins" element={<Plugins />} />
          <Route path="customers" element={<Customers />} />
          <Route path="billing" element={<Billing />} />
          <Route path="billing/invoices" element={<Billing />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="analytics" element={<Dashboard />} />
          <Route path="support" element={<Support />} />
          <Route path="inventory" element={<Inventory />} />
          <Route path="expenses" element={<Expenses />} />
          <Route path="packages" element={<Packages />} />
          <Route path="subscriptions" element={<Subscriptions />} />
          <Route path="users" element={<Users />} />
          <Route path="*" element={
            <div className="flex flex-col items-center justify-center h-64 gap-3">
              <p className="text-5xl font-bold" style={{ color: 'var(--text-secondary)' }}>404</p>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Page not found</p>
            </div>
          } />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
