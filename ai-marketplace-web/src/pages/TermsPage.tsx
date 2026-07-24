/*
 * DRAFT — not reviewed by a lawyer.
 *
 * This text was written as a working starting point. It describes how the
 * platform actually behaves today (no payment handling, AI drafts are
 * suggestions, listings are user-generated), but it has not had legal review
 * and the governing-law clause is an assumption based on the AUD pricing and
 * Australian city data.
 *
 * Before this goes in front of real users: have it reviewed, confirm the
 * jurisdiction, then delete the <DraftNotice /> block below.
 */
import type { ReactNode } from 'react'

const LAST_UPDATED = '25 July 2026'

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="mb-8">
      <h2 className="text-lg font-bold mb-3">{title}</h2>
      <div className="space-y-3 text-sm text-[var(--color-text-secondary)] leading-relaxed">{children}</div>
    </section>
  )
}

function DraftNotice() {
  return (
    <div className="mb-10 rounded-xl border border-[var(--color-accent)]/30 bg-[var(--color-accent)]/5 p-4">
      <p className="text-sm text-[var(--color-accent)] font-semibold mb-1">Draft — pending legal review</p>
      <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
        These terms are a working draft and have not been reviewed by a lawyer. They do not yet constitute the
        final agreement between you and AI Marketplace.
      </p>
    </div>
  )
}

export function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12 animate-fade-in">
      <h1 className="text-3xl font-extrabold mb-2">Terms of Service</h1>
      <p className="text-sm text-[var(--color-text-secondary)] mb-10">Last updated: {LAST_UPDATED}</p>

      <DraftNotice />

      <Section title="1. Accepting these terms">
        <p>
          By creating an account or using AI Marketplace, you agree to these terms. If you do not agree, please do
          not use the service. You must be at least 18 years old to hold an account.
        </p>
      </Section>

      <Section title="2. Your account">
        <p>
          You are responsible for the accuracy of the details you provide and for keeping your password secure.
          You are responsible for activity that occurs under your account. Tell us promptly if you believe your
          account has been accessed without your permission.
        </p>
        <p>One person or business may not maintain multiple accounts to evade limits, bans, or moderation.</p>
      </Section>

      <Section title="3. Listings and your content">
        <p>
          You keep ownership of the photos and text you upload. By publishing a listing you grant us a
          non-exclusive licence to host, resize, and display that content for the purpose of operating the
          marketplace.
        </p>
        <p>
          You are responsible for the accuracy of your listing, including its description, condition, and price —
          including where those were initially drafted by our AI. You must have the right to sell the item and the
          right to use the images you upload.
        </p>
      </Section>

      <Section title="4. AI-generated suggestions">
        <p>
          When you use the AI feature, your photos are analysed to produce a suggested title, description,
          category, brand, and price range. These are drafts. They may be wrong, incomplete, or unsuitable.
        </p>
        <p>
          Suggested prices are estimates generated from image analysis, not valuations or appraisals. You are
          responsible for reviewing and correcting anything the AI produces before you publish it, and the
          published listing is yours regardless of how it was drafted.
        </p>
      </Section>

      <Section title="5. Prohibited items and conduct">
        <p>You may not list: illegal goods, weapons, drugs, counterfeit or stolen items, live animals, recalled products, or anything you are not legally permitted to sell.</p>
        <p>
          You may not post misleading listings, harass other users through messaging, scrape the service, attempt
          to circumvent rate limits or authentication, or use the service to send unsolicited advertising.
        </p>
      </Section>

      <Section title="6. Transactions between users">
        <p>
          AI Marketplace is a listing and messaging platform. We are not a party to any sale. We do not process
          payments, hold funds, ship goods, verify items, or provide escrow. Price, payment method, handover, and
          any refund are arranged directly between buyer and seller.
        </p>
        <p>
          Because we are not part of the transaction, we cannot resolve payment disputes or guarantee that any
          item matches its listing. Please exercise the same care you would with any private sale.
        </p>
      </Section>

      <Section title="7. Moderation">
        <p>
          We may remove listings, restrict features, or suspend accounts that breach these terms or that we
          reasonably believe present a risk to other users. Where practical we will explain why. Moderation actions
          are recorded.
        </p>
      </Section>

      <Section title="8. Availability">
        <p>
          The service is provided as-is. We do not guarantee uninterrupted availability, and features may change or
          be withdrawn. We are not liable for indirect or consequential loss arising from your use of the service,
          or from any dealing with another user, to the extent permitted by law.
        </p>
      </Section>

      <Section title="9. Ending your use">
        <p>
          You may stop using the service and request deletion of your account at any time. We may close accounts
          that remain in serious or repeated breach of these terms.
        </p>
      </Section>

      <Section title="10. Changes">
        <p>
          We may update these terms. Where changes are significant we will make that clear in the service. The date
          at the top of this page reflects the most recent revision, and continuing to use the service after a
          change means you accept the revised terms.
        </p>
      </Section>

      <Section title="11. Governing law">
        <p>These terms are governed by the laws of Australia.</p>
      </Section>
    </div>
  )
}
