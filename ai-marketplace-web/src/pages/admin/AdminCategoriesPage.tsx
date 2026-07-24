import { useEffect, useState, type FormEvent } from 'react'
import { categoriesApi, adminApi } from '@/api/endpoints'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import type { Category } from '@/types'

export function AdminCategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [nameAr, setNameAr] = useState('')
  const [nameEn, setNameEn] = useState('')
  const [slug, setSlug] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  function refresh() {
    categoriesApi.list().then(setCategories)
  }

  useEffect(() => {
    refresh()
  }, [])

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    setIsSaving(true)
    try {
      await adminApi.createCategory({ name_ar: nameAr, name_en: nameEn, slug, attributes_schema: { fields: [] } })
      setNameAr('')
      setNameEn('')
      setSlug('')
      setIsFormOpen(false)
      refresh()
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-sm font-semibold text-[var(--color-text-secondary)]">الفئات الرئيسية ({categories.length})</h2>
        <Button size="sm" onClick={() => setIsFormOpen(!isFormOpen)}>{isFormOpen ? 'إلغاء' : '+ فئة جديدة'}</Button>
      </div>

      {isFormOpen && (
        <form onSubmit={handleCreate} className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
          <Input placeholder="الاسم بالعربي" required value={nameAr} onChange={(e) => setNameAr(e.target.value)} />
          <Input placeholder="الاسم بالإنجليزي" required value={nameEn} onChange={(e) => setNameEn(e.target.value)} />
          <Input placeholder="slug (مثال: furniture)" required value={slug} onChange={(e) => setSlug(e.target.value)} />
          <Button type="submit" isLoading={isSaving} className="sm:col-span-3">حفظ</Button>
        </form>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {categories.map((cat) => (
          <div key={cat.id} className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-3">
            <p className="font-medium">{cat.name_ar}</p>
            <p className="text-xs text-[var(--color-text-secondary)]">{cat.slug}</p>
          </div>
        ))}
      </div>

      <p className="text-xs text-[var(--color-text-secondary)] mt-6">
        ملاحظة: تعديل attributes_schema (حقول كل فئة) يحتاج واجهة أكثر تفصيلاً — حالياً الفئات الجديدة تُنشأ بدون حقول مخصصة، تُضاف لاحقاً عبر الـ Backend مباشرة أو توسعة هذي الشاشة.
      </p>
    </div>
  )
}
