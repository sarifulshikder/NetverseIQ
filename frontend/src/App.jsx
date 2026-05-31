import React, { useEffect, useState } from 'react'
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
import PluginPage from './pages/PluginPage.jsx'
import api from './api/client.js'

const STATIC_PAGES = {
  '':              <Dashboard />,
  'plugins':       <Plugins />,
  'customers':     <Customers />,
  'billing':       <Billing />,
  'billing/invoices': <Billing />,
  'notifications': <Notifications />,
  'analytics':     <Dashboard />,
  'support':       <Support />,
  'inventory':     <Inventory />,
  'expenses':      <Expenses />,
  'packages':      <Packages />,
  'subscriptions': <Subscriptions />,
  'users':         <Users />,
}

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

function DynamicRoutes() {
  const [pluginRoutes, setPluginRoutes] = useState([])

  useEffect(() => {
    api.get('/plugins/menu')
      .then(r => {
        const dynamic = r.data.filter(item => {
          const path = item.path.startsWith('/') ? item.path.slice(1) : item.path
          return !STATIC_PAGES.hasOwnProperty(path)
        })
        setPluginRoutes(dynamic)
      })
      .catch(() => {})
  }, [])

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
        {Object.entries(STATIC_PAGES).map(([path, element]) => (
          path === ''
            ? <Route key="index" index element={element} />
            : <Route key={path} path={path} element={element} />
        ))}
        {pluginRoutes.map(item => {
          const path = item.path.startsWith('/') ? item.path.slice(1) : item.path
          return (
            <Route key={path} path={path} element={
              <PluginPage
                pluginId={item.plugin_id || path}
                apiPrefix={item.api_prefix}
                title={item.label}
                listEndpoint={item.list_endpoint}
                fields={item.fields}
              />
            } />
          )
        })}
        <Route path="*" element={
          <div className="flex flex-col items-center justify-center h-64 gap-3">
            <p className="text-5xl font-bold" style={{ color: 'var(--text-secondary)' }}>404</p>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Page not found</p>
          </div>
        } />
      </Route>
    </Routes>
  )
}

export default function App() {
  const { init } = useAuthStore()
  const { init: initTheme } = useThemeStore()
  useEffect(() => { initTheme(); init() }, [])
  return (
    <BrowserRouter>
      <DynamicRoutes />
    </BrowserRouter>
  )
}
