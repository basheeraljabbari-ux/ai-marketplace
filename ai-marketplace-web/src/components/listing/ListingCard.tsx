import { Link } from 'react-router-dom'
import { Badge } from '@/components/common/Feedback'
import type { Listing } from '@/types'

export function ListingCard({ listing }: { listing: Listing }) {
  const cover = listing.images?.[0]?.thumbnail_url || listing.images?.[0]?.optimized_url

  return (
    <Link
      to={`/listing/${listing.id}`}
      className="group rounded-xl overflow-hidden bg-[var(--color-surface)] border border-[var(--color-border)]
        hover:border-[var(--color-accent)]/50 transition-all duration-200 hover:-translate-y-0.5"
    >
      <div className="aspect-square bg-[#141414] relative overflow-hidden">
        {cover ? (
          <img src={cover} alt={listing.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[var(--color-text-secondary)] text-3xl">◈</div>
        )}
        {listing.is_ai_generated && (
          <span className="absolute top-2 right-2">
            <Badge tone="accent">✦ AI</Badge>
          </span>
        )}
        {listing.status === 'sold' && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
            <Badge tone="danger">Sold</Badge>
          </div>
        )}
      </div>
      <div className="p-3">
        <h3 className="text-sm font-medium text-white truncate mb-1">{listing.title}</h3>
        <p className="text-[var(--color-accent)] font-bold">
          {listing.price ? `${listing.price.toLocaleString()} ${listing.currency}` : 'Contact for price'}
        </p>
      </div>
    </Link>
  )
}
