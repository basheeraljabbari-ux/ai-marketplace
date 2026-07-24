import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { adminApi } from '@/api/endpoints'
import { Button } from '@/components/common/Button'
import { Badge } from '@/components/common/Feedback'
import type { Listing } from '@/types'

const STATUS_LABELS: Record<string, string> = {
  draft: 'مسودة', active: 'نشط', sold: 'مباع', expired: 'منتهي', removed: 'محذوف',
}

export function AdminListingsPage() {
  const [listings, setListings] = useState<Listing[]>([])
  const [statusFilter, setStatusFilter] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    setIsLoading(true)
    adminApi.listListings(statusFilter || undefined).then((data) => {
      setListings(data)
      setIsLoading(false)
    })
  }, [statusFilter])

  async function handleRemove(listing: Listing) {
    const reason = prompt('سبب الحذف (اختياري):') || undefined
    if (!confirm(`متأكد تبي تحذف "${listing.title}"؟`)) return
    await adminApi.removeListing(listing.id, reason)
    setListings((prev) => prev.filter((l) => l.id !== listing.id))
  }

  return (
    <div>
      <div className="flex gap-2 mb-6">
        {['', 'active', 'draft', 'sold', 'removed'].map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
              statusFilter === s ? 'bg-[var(--color-accent)] text-[#0F0F0F] border-transparent' : 'border-[var(--color-border)] text-[var(--color-text-secondary)]'
            }`}
          >
            {s ? STATUS_LABELS[s] : 'الكل'}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-[var(--color-text-secondary)]">جاري التحميل...</p>
      ) : (
        <div className="space-y-2">
          {listings.map((listing) => (
            <div key={listing.id} className="flex items-center gap-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-3">
              <Link to={`/listing/${listing.id}`} className="w-14 h-14 rounded-lg overflow-hidden bg-[#141414] shrink-0">
                {listing.images[0]?.thumbnail_url && <img src={listing.images[0].thumbnail_url} className="w-full h-full object-cover" alt="" />}
              </Link>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{listing.title}</p>
                <p className="text-xs text-[var(--color-text-secondary)]">{listing.price ? `${listing.price} ${listing.currency}` : '—'}</p>
              </div>
              <Badge tone={listing.status === 'active' ? 'success' : listing.status === 'removed' ? 'danger' : 'default'}>
                {STATUS_LABELS[listing.status]}
              </Badge>
              {listing.status !== 'removed' && (
                <Button size="sm" variant="danger" onClick={() => handleRemove(listing)}>حذف</Button>
              )}
            </div>
          ))}
          {listings.length === 0 && <p className="text-sm text-[var(--color-text-secondary)]">ما فيه إعلانات بهذي الحالة</p>}
        </div>
      )}
    </div>
  )
}
