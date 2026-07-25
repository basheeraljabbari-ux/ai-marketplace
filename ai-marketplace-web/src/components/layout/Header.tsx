import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/common/Button'

export function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [query, setQuery] = useState('')

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    navigate(query ? `/search?q=${encodeURIComponent(query)}` : '/search')
  }

  return (
    <header className="sticky top-0 z-40 bg-[#0F0F0F]/95 backdrop-blur-sm border-b border-[var(--color-border)]">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center gap-6">
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <span className="text-[var(--color-accent)] text-2xl">◈</span>
          <span className="font-[var(--font-display)] font-bold text-lg hidden sm:block">AI Marketplace</span>
        </Link>

        <form onSubmit={handleSearch} className="flex-1 max-w-xl">
          <div className="relative">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for anything..."
              className="w-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full py-2 px-4 pl-10 text-sm
                focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent transition-colors"
            />
            <button type="submit" className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-secondary)]" aria-label="Search">
              ⌕
            </button>
          </div>
        </form>

        <div className="flex items-center gap-3 shrink-0">
          {user ? (
            <>
              <Link to="/create" className="hidden sm:block">
                <Button size="sm">+ New Listing</Button>
              </Link>
              <Link to="/messages" className="text-[var(--color-text-secondary)] hover:text-white transition-colors" aria-label="Messages">
                ✉
              </Link>
              <Link to="/favorites" className="text-[var(--color-text-secondary)] hover:text-white transition-colors" aria-label="Favorites">
                ♡
              </Link>
              <Link to="/my-listings" className="text-sm text-[var(--color-text-secondary)] hover:text-white transition-colors hidden md:block">
                My Listings
              </Link>
              <Link to="/account" className="text-sm text-[var(--color-text-secondary)] hover:text-white transition-colors hidden md:block">
                {user.full_name.split(' ')[0]}
              </Link>
              {user.role === 'admin' && (
                <Link to="/admin" className="text-sm text-[var(--color-accent)] hover:underline hidden md:block">
                  Admin
                </Link>
              )}
              <Button variant="ghost" size="sm" onClick={logout}>Log out</Button>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost" size="sm">Log in</Button>
              </Link>
              <Link to="/register">
                <Button size="sm">Sign up</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
