import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { listingsApi, categoriesApi, type SearchParams } from '@/api/endpoints'
import { ListingCard } from '@/components/listing/ListingCard'
import { ListingCardSkeleton } from '@/components/common/Feedback'
import { EmptyState } from '@/components/common/Feedback'
import { Input } from '@/components/common/Input'
import type { Listing, Category, CategoryField } from '@/types'

/* Mirrors FIXED_SEARCH_PARAMS in the backend's listings router. Anything else in
   the URL is a per-category attribute filter, both when sending the request and
   when deciding what to drop on a category change. */
const FIXED_PARAMS = new Set(['q', 'city_id', 'category_id', 'price_min', 'price_max', 'condition', 'page', 'limit'])

const controlClass = `bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-white
  focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]`

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [listings, setListings] = useState<Listing[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [categories, setCategories] = useState<Category[]>([])
  const [fields, setFields] = useState<CategoryField[]>([])

  const q = searchParams.get('q') || ''
  const priceMin = searchParams.get('price_min') || ''
  const priceMax = searchParams.get('price_max') || ''
  const categoryId = searchParams.get('category_id') || ''

  useEffect(() => {
    categoriesApi.list().then(setCategories).catch(() => setCategories([]))
  }, [])

  /* The filter controls for a category come from its schema, so they can only be
     rendered after this resolves. Guarded against out-of-order responses when the
     category is switched twice quickly. */
  useEffect(() => {
    if (!categoryId) {
      setFields([])
      return
    }
    let cancelled = false
    categoriesApi
      .attributesSchema(categoryId)
      .then((res) => !cancelled && setFields(res.fields.filter((f) => f.filterable)))
      .catch(() => !cancelled && setFields([]))
    return () => {
      cancelled = true
    }
  }, [categoryId])

  useEffect(() => {
    setIsLoading(true)
    const params: SearchParams = { limit: 24 }
    searchParams.forEach((value, key) => {
      if (!value) return
      params[key] = key === 'price_min' || key === 'price_max' ? Number(value) : value
    })
    listingsApi
      .search(params)
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

  /* Attribute filters are meaningless outside the category that defined them, so
     switching category keeps only the fixed filters and drops the rest. */
  function changeCategory(value: string) {
    const next = new URLSearchParams()
    searchParams.forEach((v, k) => {
      if (FIXED_PARAMS.has(k)) next.set(k, v)
    })
    if (value) next.set('category_id', value)
    else next.delete('category_id')
    setSearchParams(next)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-[220px_1fr] gap-8">
        {/* Filters */}
        <aside className="space-y-6">
          <div>
            <h3 className="text-sm font-semibold mb-3 text-[var(--color-text-secondary)]">Category</h3>
            <select value={categoryId} onChange={(e) => changeCategory(e.target.value)} className={`w-full ${controlClass}`}>
              <option value="">All categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name_en}</option>
              ))}
            </select>
          </div>

          <div>
            <h3 className="text-sm font-semibold mb-3 text-[var(--color-text-secondary)]">Price</h3>
            <div className="flex gap-2">
              <Input placeholder="Min" type="number" value={priceMin} onChange={(e) => updateFilter('price_min', e.target.value)} />
              <Input placeholder="Max" type="number" value={priceMax} onChange={(e) => updateFilter('price_max', e.target.value)} />
            </div>
          </div>

          {fields.map((field) => (
            <div key={field.key}>
              <h3 className="text-sm font-semibold mb-3 text-[var(--color-text-secondary)]">
                {field.label_en || field.label_ar}
              </h3>
              {field.type === 'select' ? (
                <select
                  value={searchParams.get(field.key) || ''}
                  onChange={(e) => updateFilter(field.key, e.target.value)}
                  className={`w-full ${controlClass}`}
                >
                  <option value="">Any</option>
                  {field.options?.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : (
                <Input
                  type={field.type === 'number' ? 'number' : 'text'}
                  placeholder="Any"
                  min={field.min}
                  max={field.max}
                  value={searchParams.get(field.key) || ''}
                  onChange={(e) => updateFilter(field.key, e.target.value)}
                />
              )}
            </div>
          ))}
        </aside>

        {/* Results */}
        <div>
          <div className="flex items-center justify-between mb-5">
            <h1 className="text-lg font-bold">
              {q ? `Results for "${q}"` : 'All Products'}
              {!isLoading && <span className="text-[var(--color-text-secondary)] font-normal text-sm ml-2">({total})</span>}
            </h1>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {Array.from({ length: 8 }).map((_, i) => <ListingCardSkeleton key={i} />)}
            </div>
          ) : listings.length === 0 ? (
            <EmptyState title="No results found" description="Try different keywords or adjust your filters" />
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
