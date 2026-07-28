import { Link } from 'react-router-dom'
import { Button } from '@/components/common/Button'

const STEPS = [
  {
    title: 'Snap a few photos',
    body: 'Upload up to ten photos of whatever you are selling. No forms to fill in first — the photos are the starting point.',
  },
  {
    title: 'Let the AI draft it',
    body: 'Our AI reads your photos and drafts a title, a description, the likely category and brand, and a realistic price range based on the condition you selected.',
  },
  {
    title: 'Review and publish',
    body: 'Everything the AI writes is a draft you own. Adjust anything that is not right, set your price, and publish. Your listing goes live immediately.',
  },
]

export function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12 animate-fade-in">
      <h1 className="text-3xl sm:text-4xl font-extrabold mb-4">
        Selling should take <span className="text-[var(--color-accent)]">seconds</span>, not evenings.
      </h1>
      <p className="text-[var(--color-text-secondary)] text-lg leading-relaxed mb-12">
        Most things worth selling never get listed. Not because nobody wants them, but because writing a good
        listing is tedious — a title that reads well, a description that answers the obvious questions, a price
        that is neither insulting nor optimistic. Bazo exists to remove that work.
      </p>

      <section className="mb-12">
        <h2 className="text-xl font-bold mb-6">How it works</h2>
        <ol className="space-y-6">
          {STEPS.map((step, i) => (
            <li key={step.title} className="flex gap-4">
              <span
                className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                  bg-[var(--color-accent)]/10 text-[var(--color-accent)] border border-[var(--color-accent)]/30"
                aria-hidden="true"
              >
                {i + 1}
              </span>
              <div>
                <h3 className="font-semibold mb-1">{step.title}</h3>
                <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="mb-12">
        <h2 className="text-xl font-bold mb-4">What we believe</h2>
        <div className="space-y-4 text-[var(--color-text-secondary)] leading-relaxed">
          <p>
            <span className="text-white font-medium">The AI drafts, you decide.</span> Every suggestion — title,
            description, price — is editable before anything is published. We would rather you correct a draft in
            ten seconds than start from a blank page.
          </p>
          <p>
            <span className="text-white font-medium">Price estimates are estimates.</span> The suggested range
            reflects what the AI can see in your photos and the condition you stated. It is a starting point for
            your judgement, not a valuation.
          </p>
          <p>
            <span className="text-white font-medium">Buyers and sellers talk directly.</span> Messaging is built
            in, so questions get answered without handing over your phone number or email.
          </p>
        </div>
      </section>

      <div className="flex flex-wrap items-center gap-3 pt-6 border-t border-[var(--color-border)]">
        <Link to="/create">
          <Button size="lg">Start Selling Free →</Button>
        </Link>
        <Link to="/search">
          <Button variant="secondary" size="lg">Browse Listings</Button>
        </Link>
      </div>
    </div>
  )
}
