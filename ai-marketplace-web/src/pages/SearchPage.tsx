import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { listingsApi } from '@/api/endpoints'
import { ListingCard } from '@/components/listing/ListingCard'
import { ListingCardSkeleton } from '@/components/common/Feedback'
import { EmptyState } from '@/components/common/Feedback'
import { Input } from '@/components/common/Input'
import type { Listing } from '@/types'

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [listings, setListings] = useState<Listing[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  const q = searchParams.get('q') || ''
  const priceMin = searchParams.get('price_min') || ''
  const priceMax = searchParams.get('price_max') || ''

  useEffect(() => {
    setIsLoading(true)
    listingsApi
      .search({
        q: q || undefined,
        category_id: searchParams.get('category_id') || undefined,
        price_min: priceMin ? Number(priceMin) : undefined,
        price_max: priceMax ? Number(priceMax) : undefined,
        limit: 24,
      })
      .then(async (res) => {
        setTotal(res.total)
        const details = await Promise.all(res.listing_ids.map((id) => listingsApi.get(id).catch(() => null)))
        setListings(details.filter(Boolean) as Listing[])
      })
      .finally(() => setIsLoading(false))
  }, [searchParams])

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    setSearchParams(next)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-[220px_1fr] gap-8">
        {/* Filters */}
        <aside className="space-y-6">
          <div>
            <h3 className="text-sm font-semibold mb-3 text-[var(--color-text-secondary)]">السعر</h3>
            <div className="flex gap-2">
              <Input placeholder="من" type="number" value={priceMin} onChange={(e) => updateFilter('price_min', e.target.value)} />
              <Input placeholder="لين" type="number" value={priceMax} onChange={(e) => updateFilter('price_max', e.target.value)} />
            </div>
          </div>
        </aside>

        {/* Results */}
        <div>
          <div className="flex items-center justify-between mb-5">
            <h1 className="text-lg font-bold">
              {q ? `نتائج البحث عن "${q}"` : 'كل المنتجات'}
              {!isLoading && <span className="text-[var(--color-text-secondary)] font-normal text-sm mr-2">({total})</span>}
            </h1>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {Array.from({ length: 8 }).map((_, i) => <ListingCardSkeleton key={i} />)}
            </div>
          ) : listings.length === 0 ? (
            <EmptyState title="ما فيه نتائج" description="جرب كلمات بحث ثانية أو غيّر الفلاتر" />
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {listings.map((listing) => <ListingCard key={listing.id} listing={listing} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
