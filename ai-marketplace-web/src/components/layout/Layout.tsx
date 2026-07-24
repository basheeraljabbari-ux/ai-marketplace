import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { Header } from './Header'

const FOOTER_LINKS = [
  { to: '/about', label: 'About' },
  { to: '/terms', label: 'Terms' },
  { to: '/privacy', label: 'Privacy' },
]

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-bg)] text-white">
      <Header />
      <main className="flex-1">{children}</main>
      <footer className="border-t border-[var(--color-border)] py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 flex flex-col items-center gap-3 text-sm text-[var(--color-text-secondary)]">
          <nav className="flex items-center gap-6" aria-label="Footer">
            {FOOTER_LINKS.map((link) => (
              <Link key={link.to} to={link.to} className="hover:text-white transition-colors">
                {link.label}
              </Link>
            ))}
          </nav>
          <p>AI Marketplace © 2026 — All rights reserved</p>
        </div>
      </footer>
    </div>
  )
}
