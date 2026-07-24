import { NavLink, Outlet, Navigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'

const tabs = [
  { to: '/admin', label: 'نظرة عامة', end: true },
  { to: '/admin/users', label: 'المستخدمين' },
  { to: '/admin/listings', label: 'الإعلانات' },
  { to: '/admin/categories', label: 'الفئات' },
]

export function AdminLayout() {
  const { user, isLoading } = useAuth()

  if (isLoading) return null
  if (!user || user.role !== 'admin') return <Navigate to="/" replace />

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">لوحة الإدارة</h1>
      <div className="flex gap-2 border-b border-[var(--color-border)] mb-8 overflow-x-auto">
        {tabs.map((tab) => (
          <NavLink
            key={tab.to}
            to={tab.to}
            end={tab.end}
            className={({ isActive }) =>
              `px-4 py-2.5 text-sm border-b-2 -mb-px whitespace-nowrap transition-colors ${
                isActive ? 'border-[var(--color-accent)] text-[var(--color-accent)]' : 'border-transparent text-[var(--color-text-secondary)] hover:text-white'
              }`
            }
          >
            {tab.label}
          </NavLink>
        ))}
      </div>
      <Outlet />
    </div>
  )
}
