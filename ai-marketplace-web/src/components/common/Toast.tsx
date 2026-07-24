import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'

type ToastTone = 'success' | 'error' | 'info'

interface ToastItem {
  id: number
  message: string
  tone: ToastTone
}

interface ToastApi {
  success: (message: string) => void
  error: (message: string) => void
  info: (message: string) => void
  dismiss: (id: number) => void
}

const ToastContext = createContext<ToastApi | null>(null)

const DISMISS_AFTER_MS = 4000

const toneStyles: Record<ToastTone, { icon: string; accent: string }> = {
  success: { icon: '✓', accent: 'var(--color-success)' },
  error: { icon: '✕', accent: 'var(--color-danger)' },
  info: { icon: '◈', accent: 'var(--color-accent)' },
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  const nextId = useRef(0)
  const timers = useRef(new Map<number, ReturnType<typeof setTimeout>>())

  const dismiss = useCallback((id: number) => {
    const timer = timers.current.get(id)
    if (timer) {
      clearTimeout(timer)
      timers.current.delete(id)
    }
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const push = useCallback(
    (message: string, tone: ToastTone) => {
      const id = nextId.current++
      setToasts((prev) => [...prev, { id, message, tone }])
      timers.current.set(id, setTimeout(() => dismiss(id), DISMISS_AFTER_MS))
    },
    [dismiss]
  )

  useEffect(() => {
    const pending = timers.current
    return () => {
      pending.forEach(clearTimeout)
      pending.clear()
    }
  }, [])

  const api = useMemo<ToastApi>(
    () => ({
      success: (message) => push(message, 'success'),
      error: (message) => push(message, 'error'),
      info: (message) => push(message, 'info'),
      dismiss,
    }),
    [push, dismiss]
  )

  return (
    <ToastContext.Provider value={api}>
      {children}
      <ToastViewport toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside a ToastProvider')
  return ctx
}

/* Always mounted, even when empty — the live region has to exist in the DOM
   before a toast is inserted for screen readers to announce it. */
function ToastViewport({ toasts, onDismiss }: { toasts: ToastItem[]; onDismiss: (id: number) => void }) {
  return (
    <div
      className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-[calc(100%-2rem)] max-w-sm pointer-events-none"
      aria-live="polite"
      aria-label="Notifications"
    >
      {toasts.map((toast) => {
        const { icon, accent } = toneStyles[toast.tone]
        return (
          <div
            key={toast.id}
            role="status"
            className="pointer-events-auto flex items-start gap-3 rounded-xl p-3 pr-2
              bg-[var(--color-surface)] border border-[var(--color-border)]
              shadow-lg shadow-black/40 animate-toast-in"
            style={{ borderLeftWidth: '3px', borderLeftColor: accent }}
          >
            <span
              className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs mt-0.5"
              style={{ color: accent, backgroundColor: `color-mix(in srgb, ${accent} 15%, transparent)` }}
              aria-hidden="true"
            >
              {icon}
            </span>
            <p className="flex-1 text-sm leading-relaxed text-white">{toast.message}</p>
            <button
              onClick={() => onDismiss(toast.id)}
              aria-label="Dismiss notification"
              className="shrink-0 w-6 h-6 rounded-md text-[var(--color-text-secondary)]
                hover:text-white hover:bg-[var(--color-surface-hover)] transition-colors"
            >
              ✕
            </button>
          </div>
        )
      })}
    </div>
  )
}
