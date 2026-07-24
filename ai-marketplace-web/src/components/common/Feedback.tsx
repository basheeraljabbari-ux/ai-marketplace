import type { ReactNode } from 'react'

export function Badge({ children, tone = 'default' }: { children: ReactNode; tone?: 'default' | 'success' | 'accent' | 'danger' }) {
  const tones = {
    default: 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] border-[var(--color-border)]',
    success: 'bg-[var(--color-success)]/10 text-[var(--color-success)] border-[var(--color-success)]/30',
    accent: 'bg-[var(--color-accent)]/10 text-[var(--color-accent)] border-[var(--color-accent)]/30',
    danger: 'bg-[var(--color-danger)]/10 text-[var(--color-danger)] border-[var(--color-danger)]/30',
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs border ${tones[tone]}`}>
      {children}
    </span>
  )
}

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-20 px-4">
      <div className="w-16 h-16 rounded-full bg-[var(--color-surface)] flex items-center justify-center mb-4 border border-[var(--color-border)]">
        <span className="text-2xl text-[var(--color-accent)]">◈</span>
      </div>
      <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
      {description && <p className="text-sm text-[var(--color-text-secondary)] max-w-sm mb-4">{description}</p>}
      {action}
    </div>
  )
}

export function ListingCardSkeleton() {
  return (
    <div className="rounded-xl overflow-hidden bg-[var(--color-surface)] border border-[var(--color-border)] animate-pulse">
      <div className="aspect-square bg-[var(--color-border)]" />
      <div className="p-3 space-y-2">
        <div className="h-4 bg-[var(--color-border)] rounded w-3/4" />
        <div className="h-5 bg-[var(--color-border)] rounded w-1/2" />
        <div className="h-3 bg-[var(--color-border)] rounded w-1/3" />
      </div>
    </div>
  )
}

export function CategoryPillSkeleton({ width = 'w-24' }: { width?: string }) {
  return (
    <div
      className={`shrink-0 h-9 ${width} rounded-full bg-[var(--color-surface)] border border-[var(--color-border)] animate-pulse`}
    />
  )
}

/** Shown in place of a listing photo when the listing has no images. */
export function ImagePlaceholder({ size = 'sm' }: { size?: 'sm' | 'lg' }) {
  return (
    <div className="w-full h-full relative flex flex-col items-center justify-center gap-2 bg-gradient-to-br from-[#1C1C1C] via-[#151515] to-[#0F0F0F]">
      <div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(circle at 50% 45%, color-mix(in srgb, var(--color-accent) 9%, transparent), transparent 62%)',
        }}
        aria-hidden="true"
      />
      <svg
        viewBox="0 0 48 48"
        fill="none"
        aria-hidden="true"
        className={`relative text-[var(--color-accent)] ${size === 'lg' ? 'w-16 h-16' : 'w-10 h-10'}`}
      >
        <path d="M24 4 44 24 24 44 4 24Z" stroke="currentColor" strokeOpacity="0.35" strokeWidth="2" strokeLinejoin="round" />
        <path d="M24 16 32 24 24 32 16 24Z" fill="currentColor" fillOpacity="0.3" />
      </svg>
      {size === 'lg' && <span className="relative text-xs text-[var(--color-text-secondary)]">No photo</span>}
    </div>
  )
}
