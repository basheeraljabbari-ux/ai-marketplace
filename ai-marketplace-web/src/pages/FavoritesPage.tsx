import { useEffect, useState } from 'react'
import { listingsApi, favoritesApi } from '@/api/endpoints'
import { ListingCard } from '@/components/listing/ListingCard'
import { EmptyState } from '@/components/common/Feedback'
import type { Listing } from '@/types'

export function FavoritesPage() {
  const [listings, setListings] = useState<Listing[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    favoritesApi
      .list()
      .then(async (favs: { listing_id: string }[]) => {
        const details = await Promise.all(favs.map((f) => listingsApi.get(f.listing_id).catch(() => null)))
        setListings(details.filter(Boolean) as Listing[])
      })
      .finally(() => setIsLoading(false))
  }, [])

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">المفضلة</h1>
      {isLoading ? (
        <p className="text-[var(--color-text-secondary)]">جاري التحميل...</p>
      ) : listings.length === 0 ? (
        <EmptyState title="ما فيه شي بالمفضلة" description="اضغط على قلب أي منتج تعجبك عشان تحفظه هنا" />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {listings.map((listing) => <ListingCard key={listing.id} listing={listing} />)}
        </div>
      )}
    </div>
  )
}
