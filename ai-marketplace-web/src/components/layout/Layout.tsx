import type { ReactNode } from 'react'
import { Header } from './Header'

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-bg)] text-white">
      <Header />
      <main className="flex-1">{children}</main>
      <footer className="border-t border-[var(--color-border)] py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-[var(--color-text-secondary)]">
          AI Marketplace © 2026 — All rights reserved
        </div>
      </footer>
    </div>
  )
}
