import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Input } from '@/components/common/Input'
import { Button } from '@/components/common/Button'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    setIsLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('Incorrect email or password')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto px-4 py-20">
      <h1 className="text-2xl font-bold text-center mb-1">Log In</h1>
      <p className="text-sm text-[var(--color-text-secondary)] text-center mb-8">Welcome back</p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        <Input label="Password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
        {error && <p className="text-sm text-[var(--color-danger)]">{error}</p>}
        <Button type="submit" isLoading={isLoading} className="mt-2">Log In</Button>
      </form>

      <p className="text-sm text-[var(--color-text-secondary)] text-center mt-6">
        Don't have an account? <Link to="/register" className="text-[var(--color-accent)] hover:underline">Sign up</Link>
      </p>
    </div>
  )
}
