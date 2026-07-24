import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { listingsApi } from '@/api/endpoints'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { CONDITION_LABELS, type ListingCondition } from '@/types'

type Mode = 'choose' | 'ai' | 'manual'

export function CreateListingPage() {
  const [mode, setMode] = useState<Mode>('choose')

  if (mode === 'choose') {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16">
        <h1 className="text-2xl font-bold text-center mb-2">كيف تحب تنشئ إعلانك؟</h1>
        <p className="text-[var(--color-text-secondary)] text-center mb-10">اختر الطريقة الأنسب لك</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button
            onClick={() => setMode('ai')}
            className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-accent)]/30 hover:border-[var(--color-accent)] text-right transition-colors"
          >
            <span className="text-2xl block mb-2">✦</span>
            <h3 className="font-semibold mb-1">بمساعدة الذكاء الاصطناعي</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">ارفع صور بس، ونكتب العنوان والوصف ونقترح السعر تلقائياً</p>
          </button>

          <button
            onClick={() => setMode('manual')}
            className="p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-white/30 text-right transition-colors"
          >
            <span className="text-2xl block mb-2">✎</span>
            <h3 className="font-semibold mb-1">يدوياً</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">تعبي كل التفاصيل بنفسك، تحكم كامل بكل حقل</p>
          </button>
        </div>
      </div>
    )
  }

  if (mode === 'ai') return <AICreateFlow onBack={() => setMode('choose')} />
  return <ManualCreateFlow onBack={() => setMode('choose')} />
}

// ---------- مسار AI ----------
type AIStatus = 'idle' | 'uploading' | 'queuing' | 'polling' | 'error'

function AICreateFlow({ onBack }: { onBack: () => void }) {
  const navigate = useNavigate()
  const [files, setFiles] = useState<File[]>([])
  const [condition, setCondition] = useState<ListingCondition>('used_good')
  const [status, setStatus] = useState<AIStatus>('idle')
  const [progressLabel, setProgressLabel] = useState('')
  const [errorMsg, setErrorMsg] = useState('')

  async function handleGenerate() {
    if (files.length === 0) return
    setErrorMsg('')

    try {
      // 1) ننشئ مسودة فاضية أول شي عشان يكون عندها listing_id نربط فيها الصور والـ AI job
      setStatus('uploading')
      setProgressLabel('جاري إنشاء المسودة...')
      const draft = await listingsApi.create({ title: 'مسودة قيد التحليل', condition })

      // 2) نرفع كل صورة فعلياً للـ Backend (S3) — واحدة تلو الثانية عشان نعرض تقدّم واضح
      const imageUrls: string[] = []
      for (let i = 0; i < files.length; i++) {
        setProgressLabel(`رفع الصورة ${i + 1} من ${files.length}...`)
        const img = await listingsApi.uploadImage(draft.id, files[i])
        imageUrls.push(img.optimized_url || img.original_url)
      }

      // 3) نبدأ تحليل AI فعلي على نفس المسودة، بروابط الصور الحقيقية المرفوعة
      setStatus('queuing')
      setProgressLabel('جاري إرسال الصور للتحليل...')
      const job = await listingsApi.aiGenerate(imageUrls, condition, draft.id)

      // 4) Polling لحالة الـ job
      setStatus('polling')
      setProgressLabel('يحلل الصور، يكتب العنوان والوصف، يقترح السعر...')

      const poll = setInterval(async () => {
        const result = await listingsApi.aiGenerateStatus(job.job_id)
        if (result.status === 'finished') {
          clearInterval(poll)
          navigate(`/my-listings/${result.listing_id || draft.id}/edit`)
        } else if (result.status === 'failed') {
          clearInterval(poll)
          setStatus('error')
          setErrorMsg('فشل التحليل — جرب صور أوضح أو حاول مرة ثانية')
        }
      }, 2000)
    } catch {
      setStatus('error')
      setErrorMsg('صار خطأ أثناء رفع الصور أو التحليل')
    }
  }

  const isBusy = status === 'uploading' || status === 'queuing' || status === 'polling'

  return (
    <div className="max-w-lg mx-auto px-4 py-16">
      <button onClick={onBack} className="text-sm text-[var(--color-text-secondary)] mb-6" disabled={isBusy}>← رجوع</button>
      <h1 className="text-2xl font-bold mb-6">إنشاء بالذكاء الاصطناعي</h1>

      {status === 'idle' && (
        <>
          <div className="mb-6">
            <label className="text-sm text-[var(--color-text-secondary)] block mb-2">صور المنتج (حتى 10)</label>
            <div className="grid grid-cols-4 gap-2">
              {files.map((f, i) => (
                <div key={i} className="relative aspect-square rounded-lg overflow-hidden bg-[var(--color-surface)] border border-[var(--color-border)] group">
                  <img src={URL.createObjectURL(f)} className="w-full h-full object-cover" alt="" />
                  <button
                    onClick={() => setFiles(files.filter((_, idx) => idx !== i))}
                    className="absolute top-1 left-1 w-5 h-5 rounded-full bg-black/70 text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    ✕
                  </button>
                </div>
              ))}
              {files.length < 10 && (
                <label className="aspect-square rounded-lg border-2 border-dashed border-[var(--color-border)] flex items-center justify-center cursor-pointer hover:border-[var(--color-accent)] transition-colors text-2xl text-[var(--color-text-secondary)]">
                  +
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    multiple
                    className="hidden"
                    onChange={(e) => setFiles([...files, ...Array.from(e.target.files || [])].slice(0, 10))}
                  />
                </label>
              )}
            </div>
          </div>

          <div className="mb-8">
            <label className="text-sm text-[var(--color-text-secondary)] block mb-2">حالة المنتج</label>
            <div className="flex flex-wrap gap-2">
              {(Object.keys(CONDITION_LABELS) as ListingCondition[]).map((c) => (
                <button
                  key={c}
                  onClick={() => setCondition(c)}
                  className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                    condition === c ? 'bg-[var(--color-accent)] text-[#0F0F0F] border-transparent' : 'border-[var(--color-border)] text-[var(--color-text-secondary)]'
                  }`}
                >
                  {CONDITION_LABELS[c]}
                </button>
              ))}
            </div>
          </div>

          <Button onClick={handleGenerate} disabled={files.length === 0} size="lg" className="w-full">
            تحليل بالذكاء الاصطناعي ✦
          </Button>
        </>
      )}

      {isBusy && (
        <div className="text-center py-12">
          <div className="w-10 h-10 border-2 border-[var(--color-accent)] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-[var(--color-text-secondary)]">{progressLabel}</p>
        </div>
      )}

      {status === 'error' && (
        <div className="text-center py-12">
          <p className="text-[var(--color-danger)] mb-4">{errorMsg}</p>
          <Button variant="secondary" onClick={() => setStatus('idle')}>حاول مرة ثانية</Button>
        </div>
      )}
    </div>
  )
}

// ---------- المسار اليدوي ----------
function ManualCreateFlow({ onBack }: { onBack: () => void }) {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [condition, setCondition] = useState<ListingCondition>('used_good')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      const listing = await listingsApi.create({ title, description, price: Number(price), condition })
      navigate(`/my-listings/${listing.id}/edit`)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-16">
      <button onClick={onBack} className="text-sm text-[var(--color-text-secondary)] mb-6">← رجوع</button>
      <h1 className="text-2xl font-bold mb-6">إنشاء إعلان يدوياً</h1>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input label="عنوان الإعلان" required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="مثال: آيفون 13 برو، حالة ممتازة" />

        <div className="flex flex-col gap-1.5">
          <label className="text-sm text-[var(--color-text-secondary)]">الوصف</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-white
              focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent resize-none"
            placeholder="وصّف حالة المنتج، الملحقات، سبب البيع..."
          />
        </div>

        <Input label="السعر (AUD)" type="number" required value={price} onChange={(e) => setPrice(e.target.value)} placeholder="0" />

        <div>
          <label className="text-sm text-[var(--color-text-secondary)] block mb-2">حالة المنتج</label>
          <div className="flex flex-wrap gap-2">
            {(Object.keys(CONDITION_LABELS) as ListingCondition[]).map((c) => (
              <button
                type="button"
                key={c}
                onClick={() => setCondition(c)}
                className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                  condition === c ? 'bg-[var(--color-accent)] text-[#0F0F0F] border-transparent' : 'border-[var(--color-border)] text-[var(--color-text-secondary)]'
                }`}
              >
                {CONDITION_LABELS[c]}
              </button>
            ))}
          </div>
        </div>

        <Button type="submit" isLoading={isSubmitting} size="lg" className="mt-2">
          حفظ كمسودة ومتابعة
        </Button>
      </form>
    </div>
  )
}
