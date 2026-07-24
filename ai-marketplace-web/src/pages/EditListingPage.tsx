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

  // نسخة محلية قابلة للتعديل
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
      // نحفظ آخر تعديلات أول، وبعدين ننشر — يضمن إن النشر يعتمد على أحدث نسخة بالفورم
      await listingsApi.update(id, {
        title, description, price: Number(price),
        category_id: categoryId || undefined,
        attributes,
      })
      await listingsApi.updateStatus(id, 'active')
      navigate(`/listing/${id}`)
    } catch {
      setPublishError('تأكد إن العنوان والسعر والفئة معبّاة قبل النشر')
    } finally {
      setIsPublishing(false)
    }
  }

  if (isLoading || !listing) {
    return <div className="max-w-2xl mx-auto px-4 py-20 text-center text-[var(--color-text-secondary)]">جاري التحميل...</div>
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <div className="flex items-center gap-2 mb-6">
        <h1 className="text-2xl font-bold">راجع إعلانك</h1>
        {listing.is_ai_generated && <Badge tone="accent">✦ تم التوليد بالذكاء الاصطناعي</Badge>}
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
        <Input label="العنوان" value={title} onChange={(e) => setTitle(e.target.value)} />

        <div className="flex flex-col gap-1.5">
          <label className="text-sm text-[var(--color-text-secondary)]">الوصف</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-white
              focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent resize-none"
          />
        </div>

        <Input label="السعر (AUD)" type="number" value={price} onChange={(e) => setPrice(e.target.value)} />

        <div className="flex flex-col gap-1.5">
          <label className="text-sm text-[var(--color-text-secondary)]">الفئة</label>
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-white
              focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
          >
            <option value="">اختر الفئة...</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name_ar}</option>
            ))}
          </select>
          {!categoryId && (
            <p className="text-xs text-[var(--color-danger)]">
              {listing.is_ai_generated ? 'الذكاء الاصطناعي ما قدر يحدد الفئة بثقة كافية — اختارها يدوياً' : 'الفئة مطلوبة للنشر'}
            </p>
          )}
        </div>

        {/* حقول ديناميكية حسب الفئة المختارة — attributes_schema */}
        {fields.length > 0 && (
          <div className="border border-[var(--color-border)] rounded-lg p-4 flex flex-col gap-3">
            <p className="text-sm text-[var(--color-text-secondary)]">مواصفات {categories.find((c) => c.id === categoryId)?.name_ar}</p>
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
                    <option value="">اختر...</option>
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
            حفظ كمسودة
          </Button>
          <Button onClick={handlePublish} isLoading={isPublishing} className="flex-1">
            نشر الإعلان
          </Button>
        </div>
      </div>
    </div>
  )
}
