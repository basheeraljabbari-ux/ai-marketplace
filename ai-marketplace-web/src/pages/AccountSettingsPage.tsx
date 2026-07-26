import { useEffect, useRef, useState, type FormEvent } from 'react'
import { usersApi, geoApi } from '@/api/endpoints'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { useToast } from '@/components/common/Toast'
import { useAuth } from '@/context/AuthContext'
import type { City } from '@/types'

export function AccountSettingsPage() {
  const { user, refreshUser } = useAuth()
  const toast = useToast()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [cities, setCities] = useState<City[]>([])
  const [fullName, setFullName] = useState('')
  const [phone, setPhone] = useState('')
  const [cityId, setCityId] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  useEffect(() => {
    geoApi.cities().then(setCities).catch(() => setCities([]))
  }, [])

  // Seed the form from the current user (and re-seed after refreshUser updates it).
  useEffect(() => {
    if (!user) return
    setFullName(user.full_name)
    setPhone(user.phone || '')
    setCityId(user.city_id || '')
  }, [user])

  async function handleSave(e: FormEvent) {
    e.preventDefault()
    setIsSaving(true)
    try {
      await usersApi.updateMe({ full_name: fullName, phone: phone || null, city_id: cityId || null })
      await refreshUser()
      toast.success('Changes saved')
    } catch {
      toast.error('Could not save your changes — please try again')
    } finally {
      setIsSaving(false)
    }
  }

  async function handleAvatarChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setIsUploading(true)
    try {
      await usersApi.uploadAvatar(file)
      await refreshUser()
      toast.success('Photo updated')
    } catch {
      toast.error('Could not upload photo — use a JPG, PNG, or WebP under 5MB')
    } finally {
      setIsUploading(false)
      // Clear the input so re-selecting the same file still fires onChange.
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  if (!user) return null // ProtectedRoute guards this route; render nothing until user resolves.

  const initials = user.full_name.trim().charAt(0).toUpperCase()

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">My Account</h1>

      {/* Avatar */}
      <div className="flex items-center gap-4 mb-8 pb-8 border-b border-[var(--color-border)]">
        <div className="w-20 h-20 rounded-full overflow-hidden bg-[var(--color-surface)] border border-[var(--color-border)] flex items-center justify-center shrink-0">
          {user.avatar_url ? (
            <img src={user.avatar_url} alt={user.full_name} className="w-full h-full object-cover" />
          ) : (
            <span className="text-2xl font-bold text-[var(--color-accent)]">{initials}</span>
          )}
        </div>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleAvatarChange}
            className="hidden"
          />
          <Button variant="secondary" size="sm" onClick={() => fileInputRef.current?.click()} isLoading={isUploading}>
            Change Photo
          </Button>
          <p className="text-xs text-[var(--color-text-secondary)] mt-2">JPG, PNG or WebP, up to 5MB</p>
        </div>
      </div>

      {/* Profile form */}
      <form onSubmit={handleSave} className="flex flex-col gap-4">
        <Input label="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} required />

        <Input
          label="Phone"
          type="tel"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="Optional"
        />

        <div className="flex flex-col gap-1.5">
          <label className="text-sm text-[var(--color-text-secondary)]">City</label>
          <select
            value={cityId}
            onChange={(e) => setCityId(e.target.value)}
            className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-white
              focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
          >
            <option value="">Select city...</option>
            {cities.map((c) => (
              <option key={c.id} value={c.id}>{c.name_en}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-sm text-[var(--color-text-secondary)]">Email</label>
          <input
            value={user.email}
            readOnly
            disabled
            className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5
              text-[var(--color-text-secondary)] cursor-not-allowed"
          />
        </div>

        <div className="mt-2">
          <Button type="submit" isLoading={isSaving}>Save Changes</Button>
        </div>
      </form>
    </div>
  )
}
