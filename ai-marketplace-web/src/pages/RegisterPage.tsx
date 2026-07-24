import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Input } from '@/components/common/Input'
import { Button } from '@/components/common/Button'

export function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)

    if (password.length < 8) {
      setError('كلمة المرور لازم تكون 8 أحرف على الأقل')
      return
    }

    setIsLoading(true)
    try {
      await register(email, password, fullName)
      navigate('/')
    } catch (err: any) {
      if (err?.response?.status === 409) {
        setError('هذا البريد الإلكتروني مسجّل مسبقاً')
      } else {
        setError('صار خطأ، حاول مرة ثانية')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto px-4 py-20">
      <h1 className="text-2xl font-bold text-center mb-1">إنشاء حساب</h1>
      <p className="text-sm text-[var(--color-text-secondary)] text-center mb-8">انضم وابدأ البيع والشراء</p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input label="الاسم الكامل" required value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="اسمك" />
        <Input label="البريد الإلكتروني" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        <Input label="كلمة المرور" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="8 أحرف على الأقل" />
        {error && <p className="text-sm text-[var(--color-danger)]">{error}</p>}
        <Button type="submit" isLoading={isLoading} className="mt-2">إنشاء الحساب</Button>
      </form>

      <p className="text-sm text-[var(--color-text-secondary)] text-center mt-6">
        عندك حساب؟ <Link to="/login" className="text-[var(--color-accent)] hover:underline">تسجيل الدخول</Link>
      </p>
    </div>
  )
}
