import React, { useEffect, useState } from 'react'
import {
  Users, DollarSign, FileText, Bell, TrendingUp,
  UserCheck, AlertCircle, Activity
} from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar, Legend
} from 'recharts'
import StatCard from '../components/StatCard.jsx'
import api from '../api/client.js'

export default function Dashboard() {
  const [kpis, setKpis] = useState(null)
  const [revenueTrend, setRevenueTrend] = useState([])
  const [customerGrowth, setCustomerGrowth] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      api.get('/p/analytics/dashboard'),
      api.get('/p/analytics/revenue-trend'),
      api.get('/p/analytics/customer-growth'),
    ]).then(([k, r, c]) => {
      if (k.status === 'fulfilled') setKpis(k.value.data)
      if (r.status === 'fulfilled') setRevenueTrend(r.value.data)
      if (c.status === 'fulfilled') setCustomerGrowth(c.value.data)
      setLoading(false)
    })
  }, [])

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Customers"
          value={loading ? '…' : kpis?.total_customers ?? 0}
          icon={Users}
          color="indigo"
        />
        <StatCard
          label="Active Customers"
          value={loading ? '…' : kpis?.active_customers ?? 0}
          icon={UserCheck}
          color="green"
        />
        <StatCard
          label="Total Revenue"
          value={loading ? '…' : `৳${(kpis?.total_revenue ?? 0).toLocaleString()}`}
          icon={DollarSign}
          color="blue"
        />
        <StatCard
          label="Pending Dues"
          value={loading ? '…' : `৳${(kpis?.pending_dues ?? 0).toLocaleString()}`}
          icon={AlertCircle}
          color="yellow"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        {/* Revenue Chart */}
        <div
          className="rounded-xl p-5 shadow-sm"
          style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}
        >
          <h3 className="font-semibold text-sm mb-4" style={{ color: 'var(--text-primary)' }}>
            Revenue Trend (Last 6 Months)
          </h3>
          {revenueTrend.length === 0 ? (
            <div className="h-48 flex items-center justify-center">
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                No billing data yet
              </p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={revenueTrend}>
                <defs>
                  <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} stroke="var(--text-secondary)" />
                <YAxis tick={{ fontSize: 11 }} stroke="var(--text-secondary)" />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: 8 }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#6366f1" fill="url(#revenueGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Customer Growth Chart */}
        <div
          className="rounded-xl p-5 shadow-sm"
          style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}
        >
          <h3 className="font-semibold text-sm mb-4" style={{ color: 'var(--text-primary)' }}>
            New Customers (Last 6 Months)
          </h3>
          {customerGrowth.length === 0 ? (
            <div className="h-48 flex items-center justify-center">
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                No customer data yet
              </p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={customerGrowth}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} stroke="var(--text-secondary)" />
                <YAxis tick={{ fontSize: 11 }} stroke="var(--text-secondary)" />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: 8 }}
                />
                <Bar dataKey="new_customers" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Quick Info */}
      <div
        className="rounded-xl p-5"
        style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}
      >
        <h3 className="font-semibold text-sm mb-3" style={{ color: 'var(--text-primary)' }}>
          System Status
        </h3>
        <div className="flex flex-wrap gap-3">
          {[
            { label: 'API Backend',    status: 'Online',  color: 'green' },
            { label: 'Database',       status: 'Healthy', color: 'green' },
            { label: 'Plugin System',  status: 'Active',  color: 'green' },
            { label: 'Notifications',  status: kpis?.notifications_sent > 0 ? 'Active' : 'Ready', color: 'blue' },
          ].map(s => (
            <div key={s.label}
              className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border"
              style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}
            >
              <span className={`w-2 h-2 rounded-full ${s.color === 'green' ? 'bg-green-400' : 'bg-blue-400'}`} />
              {s.label}: <span className="font-semibold ml-0.5" style={{ color: 'var(--text-primary)' }}>{s.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
