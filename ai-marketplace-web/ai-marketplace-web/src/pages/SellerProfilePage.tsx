import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { usersApi } from '@/api/endpoints'
import { ListingCard } from '@/components/listing/ListingCard'
import { EmptyState, ListingCardSkeleton } from '@/components/common/Feedback'
import type { Listing, User } from '@/types'

export function SellerProfilePage() {
  const { id } = useParams<{ id: string }>()
  const [seller, setSeller] = useState<User | null>(null)
  const [listings, setListings] = useState<Listing[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    if (!id) return
    setIsLoading(true)
    setNotFound(false)
    Promise.all([usersApi.getPublic(id), usersApi.getListings(id)])
      .then(([user, userListings]) => {
        setSeller(user)
        setListings(userListings)
      })
      .catch(() => setNotFound(true))
      .finally(() => setIsLoading(false))
  }, [id])

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-10">
        <div className="flex items-center gap-4 mb-10 animate-pulse">
          <div className="w-20 h-20 rounded-full bg-[var(--color-surface)]" />
          <div className="space-y-2">
            <div className="h-5 w-40 bg-[var(--color-surface)] rounded" />
            <div className="h-4 w-24 bg-[var(--color-surface)] rounded" />
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => <ListingCardSkeleton key={i} />)}
        </div>
      </div>
    )
  }

  if (notFound || !seller) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-10">
        <EmptyState title="Seller not found" description="This link is invalid or the account was deleted" />
      </div>
    )
  }

  const initials = seller.full_name.trim().charAt(0).toUpperCase()
  const joinDate = new Date(seller.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long' })

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="flex items-center gap-4 mb-4 pb-8 border-b border-[var(--color-border)]">
        <div className="w-20 h-20 rounded-full overflow-hidden bg-[var(--color-surface)] border border-[var(--color-border)] flex items-center justify-center shrink-0">
          {seller.avatar_url ? (
            <img src={seller.avatar_url} alt={seller.full_name} className="w-full h-full object-cover" />
          ) : (
            <span className="text-2xl font-bold text-[var(--color-accent)]">{initials}</span>
          )}
        </div>
        <div>
          <h1 className="text-xl font-bold mb-1">{seller.full_name}</h1>
          <div className="flex items-center gap-3 text-sm text-[var(--color-text-secondary)]">
            {seller.rating_count > 0 ? (
              <span className="flex items-center gap-1">
                <span className="text-[var(--color-accent)]">★</span>
                {seller.rating_avg.toFixed(1)} ({seller.rating_count} reviews)
              </span>
            ) : (
              <span>No reviews yet</span>
            )}
            <span>·</span>
            <span>Member since {joinDate}</span>
          </div>
        </div>
      </div>

      <h2 className="text-lg font-bold mb-5">
        {seller.full_name.split(' ')[0]}'s Listings
        <span className="text-[var(--color-text-secondary)] font-normal text-sm ml-2">({listings.length})</span>
      </h2>

      {listings.length === 0 ? (
        <EmptyState title="No active listings right now" />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {listings.map((listing) => <ListingCard key={listing.id} listing={listing} />)}
        </div>
      )}

      <div className="mt-8">
        <Link to="/search" className="text-sm text-[var(--color-accent)] hover:underline">← Back to search</Link>
      </div>
    </div>
  )
}
