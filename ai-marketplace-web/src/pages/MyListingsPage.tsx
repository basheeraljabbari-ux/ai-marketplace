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
      alert('This listing is missing required info — complete category and price before publishing')
    }
  }

  async function handleMarkSold(id: string) {
    const updated = await listingsApi.updateStatus(id, 'sold')
    setListings((prev) => prev.map((l) => (l.id === id ? updated : l)))
  }

  async function handleDelete(id: string) {
    if (!confirm('Are you sure you want to delete this listing?')) return
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
        <h1 className="text-2xl font-bold">My Listings</h1>
        <Link to="/create"><Button>+ New Listing</Button></Link>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-10">
        {[
          { label: 'Active', value: stats.active },
          { label: 'Drafts', value: stats.draft },
          { label: 'Sold', value: stats.sold },
          { label: 'Total Views', value: stats.views },
        ].map((s) => (
          <div key={s.label} className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
            <p className="text-2xl font-bold text-[var(--color-accent)]">{s.value}</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {isLoading ? (
        <p className="text-[var(--color-text-secondary)]">Loading...</p>
      ) : listings.length === 0 ? (
        <EmptyState
          title="You don't have any listings yet"
          description="Post your first listing and start selling"
          action={<Link to="/create"><Button>Create Listing</Button></Link>}
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
                    {{ draft: 'Draft', active: 'Active', sold: 'Sold', expired: 'Expired', removed: 'Removed' }[listing.status]}
                  </Badge>
                  <span className="text-xs text-[var(--color-text-secondary)]">{listing.view_count} views</span>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {listing.status === 'draft' && <Button size="sm" onClick={() => handlePublish(listing.id)}>Publish</Button>}
                {listing.status === 'active' && <Button size="sm" variant="secondary" onClick={() => handleMarkSold(listing.id)}>Mark as Sold</Button>}
                <Button size="sm" variant="ghost" onClick={() => handleDelete(listing.id)}>Delete</Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
