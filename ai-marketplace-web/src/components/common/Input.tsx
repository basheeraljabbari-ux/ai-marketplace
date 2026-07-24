import { type InputHTMLAttributes, forwardRef } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', id, ...props }, ref) => {
    const inputId = id || props.name

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm text-[var(--color-text-secondary)]">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`
            bg-[var(--color-surface)] border rounded-lg px-4 py-2.5 text-white
            placeholder:text-[var(--color-text-secondary)]
            focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent
            transition-colors
            ${error ? 'border-[var(--color-danger)]' : 'border-[var(--color-border)]'}
            ${className}
          `}
          {...props}
        />
        {error && <span className="text-xs text-[var(--color-danger)]">{error}</span>}
      </div>
    )
  }
)
Input.displayName = 'Input'
