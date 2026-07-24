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
