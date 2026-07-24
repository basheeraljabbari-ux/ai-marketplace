import { useEffect, useState } from 'react'
import { adminApi, type AdminStats } from '@/api/endpoints'

export function AdminOverviewPage() {
  const [stats, setStats] = useState<AdminStats | null>(null)

  useEffect(() => {
    adminApi.stats().then(setStats)
  }, [])

  if (!stats) return <p className="text-[var(--color-text-secondary)]">Loading...</p>

  const cards = [
    { label: 'Total Users', value: stats.total_users },
    { label: 'Total Listings', value: stats.total_listings },
    { label: 'Active Listings', value: stats.active_listings },
    { label: "Today's Listings", value: stats.listings_today },
  ]

  return (
    <div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-10">
        {cards.map((c) => (
          <div key={c.label} className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
            <p className="text-2xl font-bold text-[var(--color-accent)]">{c.value}</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">{c.label}</p>
          </div>
        ))}
      </div>

      <h2 className="text-sm font-semibold text-[var(--color-text-secondary)] mb-3">Top Categories</h2>
      <div className="space-y-2">
        {stats.top_categories.map((cat) => (
          <div key={cat.name} className="flex items-center justify-between bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-3">
            <span>{cat.name}</span>
            <span className="text-[var(--color-accent)] font-semibold">{cat.count} listings</span>
          </div>
        ))}
        {stats.top_categories.length === 0 && <p className="text-sm text-[var(--color-text-secondary)]">Not enough data yet</p>}
      </div>
    </div>
  )
}
