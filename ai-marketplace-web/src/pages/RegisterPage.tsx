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
      setError('Password must be at least 8 characters')
      return
    }

    setIsLoading(true)
    try {
      await register(email, password, fullName)
      navigate('/')
    } catch (err: any) {
      if (err?.response?.status === 409) {
        setError('This email is already registered')
      } else {
        setError('Something went wrong, please try again')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto px-4 py-20">
      <h1 className="text-2xl font-bold text-center mb-1">Join Bazo</h1>
      <p className="text-sm text-[var(--color-text-secondary)] text-center mb-8">Your next sale is one photo away</p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input label="Full name" required value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Your name" />
        <Input label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        <Input label="Password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" />
        {error && <p className="text-sm text-[var(--color-danger)]">{error}</p>}
        <Button type="submit" isLoading={isLoading} className="mt-2">Create Account</Button>
      </form>

      <p className="text-sm text-[var(--color-text-secondary)] text-center mt-6">
        Already have an account? <Link to="/login" className="text-[var(--color-accent)] hover:underline">Log in</Link>
      </p>
    </div>
  )
}
