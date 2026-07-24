import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '@/api/client'
import { listingsApi } from '@/api/endpoints'
import { EmptyState, Badge } from '@/components/common/Feedback'
import { Button } from '@/components/common/Button'
import { useAuth } from '@/context/AuthContext'
import type { Listing } from '@/types'

export function MyListingsPage() {
  const { user } = useAuth()
  const [listings, setListings] = useState<Listing[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    api.get<Listing[]>(`/users/${user.id}/listings`).then((res) => {
      setListings(res.data)
      setIsLoading(false)
    })
  }, [user])

  async function handlePublish(id: string) {
    try {
      const updated = await listingsApi.updateStatus(id, 'active')
      setListings((prev) => prev.map((l) => (l.id === id ? updated : l)))
    } catch {
      alert('الإعلان ناقص بيانات — أكمل الفئة والسعر قبل النشر')
    }
  }

  async function handleMarkSold(id: string) {
    const updated = await listingsApi.updateStatus(id, 'sold')
    setListings((prev) => prev.map((l) => (l.id === id ? updated : l)))
  }

  async function handleDelete(id: string) {
    if (!confirm('متأكد تبي تحذف هذا الإعلان؟')) return
    await listingsApi.remove(id)
    setListings((prev) => prev.filter((l) => l.id !== id))
  }

  const stats = {
    active: listings.filter((l) => l.status === 'active').length,
    draft: listings.filter((l) => l.status === 'draft').length,
    sold: listings.filter((l) => l.status === 'sold').length,
    views: listings.reduce((sum, l) => sum + l.view_count, 0),
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">إعلاناتي</h1>
        <Link to="/create"><Button>+ إعلان جديد</Button></Link>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-10">
        {[
          { label: 'نشطة', value: stats.active },
          { label: 'مسودات', value: stats.draft },
          { label: 'مباعة', value: stats.sold },
          { label: 'إجمالي المشاهدات', value: stats.views },
        ].map((s) => (
          <div key={s.label} className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
            <p className="text-2xl font-bold text-[var(--color-accent)]">{s.value}</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {isLoading ? (
        <p className="text-[var(--color-text-secondary)]">جاري التحميل...</p>
      ) : listings.length === 0 ? (
        <EmptyState
          title="ما عندك إعلانات بعد"
          description="انشر أول إعلان لك وابدأ البيع"
          action={<Link to="/create"><Button>إنشاء إعلان</Button></Link>}
        />
      ) : (
        <div className="space-y-3">
          {listings.map((listing) => (
            <div key={listing.id} className="flex items-center gap-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-3">
              <Link to={`/listing/${listing.id}`} className="w-16 h-16 rounded-lg overflow-hidden bg-[#141414] shrink-0">
                {listing.images[0]?.thumbnail_url && <img src={listing.images[0].thumbnail_url} className="w-full h-full object-cover" alt="" />}
              </Link>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{listing.title}</p>
                <div className="flex items-center gap-2 mt-1">
                  <Badge tone={listing.status === 'active' ? 'success' : listing.status === 'sold' ? 'danger' : 'default'}>
                    {{ draft: 'مسودة', active: 'نشط', sold: 'مباع', expired: 'منتهي', removed: 'محذوف' }[listing.status]}
                  </Badge>
                  <span className="text-xs text-[var(--color-text-secondary)]">{listing.view_count} مشاهدة</span>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {listing.status === 'draft' && <Button size="sm" onClick={() => handlePublish(listing.id)}>نشر</Button>}
                {listing.status === 'active' && <Button size="sm" variant="secondary" onClick={() => handleMarkSold(listing.id)}>تمييز كمباع</Button>}
                <Button size="sm" variant="ghost" onClick={() => handleDelete(listing.id)}>حذف</Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
