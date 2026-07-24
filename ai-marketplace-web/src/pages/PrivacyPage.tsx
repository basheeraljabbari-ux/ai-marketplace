/*
 * DRAFT — not reviewed by a lawyer.
 *
 * The factual claims here were written against the actual data model and
 * request flow (app/modules/users/models.py, listings, messaging, favorites,
 * admin audit logs, the R2 storage service, and the Anthropic image analysis
 * path). They are accurate as of this commit.
 *
 * Two things still need a human decision before this is published:
 *   - the contact address in "Contacting us" is a placeholder
 *   - retention periods are described as behaviour, not fixed durations
 *
 * Keep this page in step with the code: if a new third party starts receiving
 * user data, it belongs in the "Who else processes your data" table.
 * Once reviewed, delete the <DraftNotice /> block below.
 */
import type { ReactNode } from 'react'

const LAST_UPDATED = '25 July 2026'

const PROCESSORS = [
  { name: 'Anthropic', purpose: 'Analyses listing photos to draft titles, descriptions, and price ranges — only when you use the AI feature.' },
  { name: 'Cloudflare R2', purpose: 'Stores uploaded listing images and serves them publicly on your listing.' },
  { name: 'Railway', purpose: 'Hosts the application, database, and background job queue.' },
]

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
      <p className="text-sm text-[var(--color-accent)] font-semibold mb-1">Draft — pending review</p>
      <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
        This policy accurately describes how the service handles data today, but it has not had legal review and
        the contact address below is a placeholder.
      </p>
    </div>
  )
}

export function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12 animate-fade-in">
      <h1 className="text-3xl font-extrabold mb-2">Privacy Policy</h1>
      <p className="text-sm text-[var(--color-text-secondary)] mb-10">Last updated: {LAST_UPDATED}</p>

      <DraftNotice />

      <Section title="What we collect">
        <p>
          <span className="text-white font-medium">When you register:</span> your email address, your name, and a
          password. The password is stored only as a hash — we never store or have access to the password itself.
        </p>
        <p>
          <span className="text-white font-medium">Optionally, on your profile:</span> a phone number, a profile
          picture, your city, and your preferred language. These are not required to use the service.
        </p>
        <p>
          <span className="text-white font-medium">When you list an item:</span> the photos you upload and the
          listing details — title, description, price, condition, category attributes, and location.
        </p>
        <p>
          <span className="text-white font-medium">When you use the service:</span> messages you send to other
          users, listings you favourite, view counts on your listings, and timestamps for account creation, last
          login, and last activity.
        </p>
      </Section>

      <Section title="What we do not collect">
        <p>
          We do not process payments, so we never receive your card or bank details. We do not use advertising
          trackers or third-party analytics cookies. Sessions are maintained with access and refresh tokens rather
          than tracking cookies.
        </p>
      </Section>

      <Section title="How your photos are used">
        <p>
          Listing photos are stored in object storage and served publicly as part of your listing — anyone with the
          image link can view them, including people who are not signed in. Treat anything visible in a photo as
          public, and avoid capturing documents, number plates, or your address.
        </p>
        <p>
          If you use the AI drafting feature, the photos for that listing are sent to Anthropic's API to be
          analysed. Only the images and the condition you selected are sent; your name, email, and contact details
          are not.
        </p>
      </Section>

      <Section title="What is visible to others">
        <p>
          Published listings are public, including their photos, description, price, and the city you selected.
          Your display name, profile picture, and seller rating are shown on your listings and public profile.
        </p>
        <p>
          Your email address and phone number are never shown on a listing. Messages are visible only to you and
          the other participant, though administrators can access them where necessary to investigate abuse.
        </p>
      </Section>

      <Section title="Who else processes your data">
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="text-left text-[var(--color-text-secondary)] border-b border-[var(--color-border)]">
                <th className="py-2 pr-4 font-medium">Service</th>
                <th className="py-2 font-medium">Purpose</th>
              </tr>
            </thead>
            <tbody>
              {PROCESSORS.map((p) => (
                <tr key={p.name} className="border-b border-[var(--color-border)]">
                  <td className="py-3 pr-4 text-white whitespace-nowrap align-top">{p.name}</td>
                  <td className="py-3 align-top">{p.purpose}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p>We do not sell your personal information.</p>
      </Section>

      <Section title="How long we keep it">
        <p>
          Your account and listings are kept while your account is open. Deleted listings are marked as removed and
          their images are deleted from storage at the time of deletion.
        </p>
        <p>
          Records of moderation actions — such as an account suspension and its reason — are retained after the
          fact so that decisions remain auditable.
        </p>
      </Section>

      <Section title="Security">
        <p>
          Passwords are hashed, traffic is served over HTTPS, and sensitive actions require a valid session token.
          Sign-in attempts and AI requests are rate limited to reduce abuse. No system is perfectly secure, and we
          cannot guarantee absolute security of information transmitted to the service.
        </p>
      </Section>

      <Section title="Your choices">
        <p>
          You can view and update your profile details at any time, edit or delete your listings, and request
          deletion of your account. Where deletion would remove records we are required to retain — such as
          moderation history — we will tell you.
        </p>
      </Section>

      <Section title="Contacting us">
        <p>
          For any question about this policy or the data we hold about you, contact us at{' '}
          <span className="text-white">privacy@example.com</span>.
        </p>
      </Section>
    </div>
  )
}
