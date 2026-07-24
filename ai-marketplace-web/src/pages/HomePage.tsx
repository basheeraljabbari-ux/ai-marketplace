import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { categoriesApi, listingsApi } from '@/api/endpoints'
import { ListingCard } from '@/components/listing/ListingCard'
import { ListingCardSkeleton } from '@/components/common/Feedback'
import { Button } from '@/components/common/Button'
import type { Category, Listing } from '@/types'

export function HomePage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [recent, setRecent] = useState<Listing[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      categoriesApi.list(),
      listingsApi.search({ limit: 8 }).then(async (res) => {
        // نجيب تفاصيل أول 8 نتائج لعرضها ككروت — بالتنفيذ النهائي يكون هذا endpoint واحد مجمّع
        const details = await Promise.all(res.listing_ids.slice(0, 8).map((id) => listingsApi.get(id).catch(() => null)))
        return details.filter(Boolean) as Listing[]
      }),
    ])
      .then(([cats, listings]) => {
        setCategories(cats.filter((c: Category) => !c.parent_id))
        setRecent(listings)
      })
      .finally(() => setIsLoading(false))
  }, [])

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-[var(--color-border)]">
        <div className="absolute inset-0 bg-gradient-to-b from-[var(--color-accent)]/5 to-transparent" />
        <div className="relative max-w-7xl mx-auto px-4 py-20 sm:py-28 text-center">
          <h1 className="font-[var(--font-display)] text-4xl sm:text-6xl font-extrabold mb-4 leading-tight">
            بيع واشترِ <span className="text-[var(--color-accent)]">بذكاء</span>
          </h1>
          <p className="text-[var(--color-text-secondary)] text-lg max-w-xl mx-auto mb-8">
            ارفع صور منتجك، والذكاء الاصطناعي يكتب العنوان والوصف ويقترح السعر — إعلانك جاهز خلال دقيقة.
          </p>
          <div className="flex items-center justify-center gap-3">
            <Link to="/create">
              <Button size="lg">انشر إعلانك الآن ↖</Button>
            </Link>
            <Link to="/search">
              <Button variant="secondary" size="lg">تصفح المنتجات</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="max-w-7xl mx-auto px-4 py-10">
        <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-none">
          <Link to="/search" className="shrink-0 px-4 py-2 rounded-full bg-[var(--color-accent)] text-[#0F0F0F] text-sm font-semibold">
            كل الفئات
          </Link>
          {categories.map((cat) => (
            <Link
              key={cat.id}
              to={`/search?category_id=${cat.id}`}
              className="shrink-0 px-4 py-2 rounded-full bg-[var(--color-surface)] border border-[var(--color-border)] text-sm hover:border-[var(--color-accent)]/50 transition-colors"
            >
              {cat.name_ar}
            </Link>
          ))}
        </div>
      </section>

      {/* Recent listings */}
      <section className="max-w-7xl mx-auto px-4 pb-20">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xl font-bold">أحدث المنتجات</h2>
          <Link to="/search" className="text-sm text-[var(--color-accent)] hover:underline">شوف الكل ←</Link>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {isLoading
            ? Array.from({ length: 8 }).map((_, i) => <ListingCardSkeleton key={i} />)
            : recent.map((listing) => <ListingCard key={listing.id} listing={listing} />)}
        </div>
      </section>
    </div>
  )
}
