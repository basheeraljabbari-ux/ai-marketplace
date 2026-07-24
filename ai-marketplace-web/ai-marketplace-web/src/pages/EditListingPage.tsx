import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { listingsApi, categoriesApi } from '@/api/endpoints'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { Badge } from '@/components/common/Feedback'
import type { Category, CategoryField, Listing } from '@/types'

export function EditListingPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [listing, setListing] = useState<Listing | null>(null)
  const [categories, setCategories] = useState<Category[]>([])
  const [fields, setFields] = useState<CategoryField[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isPublishing, setIsPublishing] = useState(false)
  const [publishError, setPublishError] = useState('')

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [attributes, setAttributes] = useState<Record<string, string>>({})

  useEffect(() => {
    if (!id) return
    Promise.all([listingsApi.get(id), categoriesApi.list()]).then(([l, cats]) => {
      setListing(l)
      setCategories(cats)
      setTitle(l.title)
      setDescription(l.description || '')
      setPrice(l.price ? String(l.price) : '')
      setCategoryId(l.category_id || '')
      setAttributes(l.attributes as Record<string, string>)
      setIsLoading(false)
    })
  }, [id])

  useEffect(() => {
    if (!categoryId) {
      setFields([])
      return
    }
    categoriesApi.attributesSchema(categoryId).then((res) => setFields(res.fields))
  }, [categoryId])

  async function handleSave() {
    if (!id) return
    setIsSaving(true)
    try {
      const updated = await listingsApi.update(id, {
        title, description, price: Number(price),
        category_id: categoryId || undefined,
        attributes,
      })
      setListing(updated)
    } finally {
      setIsSaving(false)
    }
  }

  async function handlePublish() {
    if (!id) return
    setPublishError('')
    setIsPublishing(true)
    try {
      await listingsApi.update(id, {
        title, description, price: Number(price),
        category_id: categoryId || undefined,
        attributes,
      })
      await listingsApi.updateStatus(id, 'active')
      navigate(`/listing/${id}`)
    } catch {
      setPublishError('Make sure title, price, and category are filled in before publishing')
    } finally {
      setIsPublishing(false)
    }
  }

  if (isLoading || !listing) {
    return <div className="max-w-2xl mx-auto px-4 py-20 text-center text-[var(--color-text-secondary)]">Loading...</div>
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <div className="flex items-center gap-2 mb-6">
        <h1 className="text-2xl font-bold">Review Your Listing</h1>
        {listing.is_ai_generated && <Badge tone="accent">✦ AI Generated</Badge>}
      </div>

      {listing.images.length > 0 && (
        <div className="flex gap-2 mb-8 overflow-x-auto">
          {listing.images.map((img) => (
            <div key={img.id} className="w-20 h-20 rounded-lg overflow-hidden bg-[var(--color-surface)] border border-[var(--color-border)] shrink-0">
              {img.thumbnail_url && <img src={img.thumbnail_url} className="w-full h-full object-cover" alt="" />}
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-col gap-4">
        <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} />

        <div className="flex flex-col gap-1.5">
          <label className="text-sm text-[var(--color-text-secondary)]">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-white
              focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent resize-none"
          />
        </div>

        <Input label="Price (AUD)" type="number" value={price} onChange={(e) => setPrice(e.target.value)} />

        <div className="flex flex-col gap-1.5">
          <label className="text-sm text-[var(--color-text-secondary)]">Category</label>
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-white
              focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
          >
            <option value="">Select category...</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name_en}</option>
            ))}
          </select>
          {!categoryId && (
            <p className="text-xs text-[var(--color-danger)]">
              {listing.is_ai_generated ? "AI couldn't confidently determine the category — please select it manually" : 'Category is required to publish'}
            </p>
          )}
        </div>

        {fields.length > 0 && (
          <div className="border border-[var(--color-border)] rounded-lg p-4 flex flex-col gap-3">
            <p className="text-sm text-[var(--color-text-secondary)]">{categories.find((c) => c.id === categoryId)?.name_en} specifications</p>
            {fields.map((field) => (
              <div key={field.key} className="flex flex-col gap-1.5">
                <label className="text-sm text-[var(--color-text-secondary)]">
                  {field.label_ar} {field.required && <span className="text-[var(--color-danger)]">*</span>}
                </label>
                {field.type === 'select' ? (
                  <select
                    value={attributes[field.key] || ''}
                    onChange={(e) => setAttributes({ ...attributes, [field.key]: e.target.value })}
                    className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-white"
                  >
                    <option value="">Select...</option>
                    {field.options?.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
                  </select>
                ) : (
                  <input
                    type={field.type === 'number' ? 'number' : 'text'}
                    value={attributes[field.key] || ''}
                    onChange={(e) => setAttributes({ ...attributes, [field.key]: e.target.value })}
                    min={field.min}
                    max={field.max}
                    className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-white
                      focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
                  />
                )}
              </div>
            ))}
          </div>
        )}

        {publishError && <p className="text-sm text-[var(--color-danger)]">{publishError}</p>}

        <div className="flex gap-3 mt-4">
          <Button variant="secondary" onClick={handleSave} isLoading={isSaving} className="flex-1">
            Save as Draft
          </Button>
          <Button onClick={handlePublish} isLoading={isPublishing} className="flex-1">
            Publish Listing
          </Button>
        </div>
      </div>
    </div>
  )
}
