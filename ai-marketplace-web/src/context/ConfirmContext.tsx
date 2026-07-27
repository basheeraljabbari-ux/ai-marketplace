import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { Button } from '@/components/common/Button'

interface ConfirmOptions {
  title?: string
  message: string
  confirmLabel?: string
  danger?: boolean
}

type ConfirmFn = (options: ConfirmOptions | string) => Promise<boolean>

const ConfirmContext = createContext<ConfirmFn | null>(null)

export function ConfirmProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ConfirmOptions | null>(null)
  const resolveRef = useRef<((value: boolean) => void) | undefined>(undefined)

  const confirmFn = useCallback<ConfirmFn>((options) => {
    const normalized = typeof options === 'string' ? { message: options } : options
    setState(normalized)
    return new Promise((resolve) => {
      resolveRef.current = resolve
    })
  }, [])

  const handle = useCallback((result: boolean) => {
    setState(null)
    resolveRef.current?.(result)
  }, [])

  useEffect(() => {
    if (!state) return
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') handle(false)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [state, handle])

  return (
    <ConfirmContext.Provider value={confirmFn}>
      {children}
      {state && (
        <div
          className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in"
          onClick={(event) => {
            if (event.target === event.currentTarget) handle(false)
          }}
        >
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 shadow-2xl">
            <h2 className="text-lg font-semibold mb-2">{state.title || 'Are you sure?'}</h2>
            <p className="text-sm text-[var(--color-text-secondary)] mb-6">{state.message}</p>
            <div className="flex gap-3">
              <Button variant="secondary" className="flex-1" onClick={() => handle(false)}>Cancel</Button>
              <Button variant={state.danger ? 'danger' : 'primary'} className="flex-1" onClick={() => handle(true)}>
                {state.confirmLabel || 'Confirm'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </ConfirmContext.Provider>
  )
}

export function useConfirm(): ConfirmFn {
  const ctx = useContext(ConfirmContext)
  if (!ctx) throw new Error('useConfirm must be used within ConfirmProvider')
  return ctx
}
