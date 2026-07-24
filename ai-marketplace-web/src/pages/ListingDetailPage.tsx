import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { listingsApi, messagingApi, favoritesApi } from '@/api/endpoints'
import { Button } from '@/components/common/Button'
import { Badge } from '@/components/common/Feedback'
import { useAuth } from '@/context/AuthContext'
import { CONDITION_LABELS, type Listing, type ListingCondition } from '@/types'

export function ListingDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [listing, setListing] = useState<Listing | null>(null)
  const [activeImage, setActiveImage] = useState(0)
  const [isStartingChat, setIsStartingChat] = useState(false)
  const [isFavorited, setIsFavorited] = useState(false)

  useEffect(() => {
    if (!id) return
    listingsApi.get(id).then(setListing)
  }, [id])

  async function handleContactSeller() {
    if (!user) {
      navigate('/login')
      return
    }
    if (!listing) return
    setIsStartingChat(true)
    try {
      const conv = await messagingApi.startConversation(listing.id)
      navigate(`/messages/${conv.id}`)
    } finally {
      setIsStartingChat(false)
    }
  }

  async function toggleFavorite() {
    if (!user) {
      navigate('/login')
      return
    }
    if (!listing) return
    if (isFavorited) {
      await favoritesApi.remove(listing.id)
    } else {
      await favoritesApi.add(listing.id)
    }
    setIsFavorited(!isFavorited)
  }

  if (!listing) {
    return <div className="max-w-5xl mx-auto px-4 py-20 text-center text-[var(--color-text-secondary)]">جاري التحميل...</div>
  }

  const images = listing.images.length ? listing.images : [null]
  const activeUrl = images[activeImage]?.optimized_url || images[activeImage]?.original_url

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Images */}
        <div>
          <div className="aspect-square rounded-xl overflow-hidden bg-[var(--color-surface)] border border-[var(--color-border)] mb-3">
            {activeUrl ? (
              <img src={activeUrl} alt={listing.title} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-4xl text-[var(--color-text-secondary)]">◈</div>
            )}
          </div>
          {images.length > 1 && (
            <div className="flex gap-2">
              {images.map((img: (typeof images)[number], i: number) => (
                <button
                  key={i}
                  onClick={() => setActiveImage(i)}
                  className={`w-16 h-16 rounded-lg overflow-hidden border-2 transition-colors ${
                    activeImage === i ? 'border-[var(--color-accent)]' : 'border-transparent'
                  }`}
                >
                  {img?.thumbnail_url && <img src={img.thumbnail_url} className="w-full h-full object-cover" alt="" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div>
          <div className="flex items-start justify-between gap-3 mb-2">
            <h1 className="text-2xl font-bold">{listing.title}</h1>
            <button onClick={toggleFavorite} aria-label="أضف للمفضلة" className="text-2xl shrink-0">
              {isFavorited ? '♥' : '♡'}
            </button>
          </div>
          <p className="text-3xl font-bold text-[var(--color-accent)] mb-4">
            {listing.price ? `${listing.price.toLocaleString()} ${listing.currency}` : 'السعر عند التواصل'}
          </p>

          <div className="flex gap-2 mb-6">
            {listing.condition && <Badge>{CONDITION_LABELS[listing.condition as ListingCondition] || listing.condition}</Badge>}
            {listing.is_ai_generated && <Badge tone="accent">✦ منشأ بالذكاء الاصطناعي</Badge>}
          </div>

          <Button onClick={handleContactSeller} isLoading={isStartingChat} size="lg" className="w-full mb-6">
            مراسلة البائع
          </Button>

          {listing.description && (
            <div className="mb-6">
              <h2 className="text-sm font-semibold text-[var(--color-text-secondary)] mb-2">الوصف</h2>
              <p className="text-white leading-relaxed whitespace-pre-line">{listing.description}</p>
            </div>
          )}

          {Object.keys(listing.attributes).length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-[var(--color-text-secondary)] mb-2">المواصفات</h2>
              <dl className="grid grid-cols-2 gap-3">
                {Object.entries(listing.attributes).map(([key, value]) => (
                  <div key={key} className="bg-[var(--color-surface)] rounded-lg px-3 py-2 border border-[var(--color-border)]">
                    <dt className="text-xs text-[var(--color-text-secondary)]">{key}</dt>
                    <dd className="text-sm">{String(value)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
