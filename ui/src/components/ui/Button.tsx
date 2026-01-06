import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
type Size = 'sm' | 'md' | 'lg'

function cx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(' ')
}

export default function Button(
  props: ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: Variant
    size?: Size
    leftIcon?: ReactNode
  },
) {
  const { variant = 'primary', size = 'md', leftIcon, className, children, ...rest } = props

  const base =
    'inline-flex items-center justify-center gap-2 rounded-md border font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500/40 disabled:opacity-50 disabled:pointer-events-none'

  const variants: Record<Variant, string> = {
    primary: 'border-teal-700 bg-teal-700 text-white hover:bg-teal-800',
    secondary: 'border-slate-200 bg-slate-100 text-slate-900 hover:bg-slate-200',
    outline: 'border-slate-300 bg-white text-slate-900 hover:bg-slate-50',
    ghost: 'border-transparent bg-transparent text-slate-700 hover:bg-slate-100',
    danger: 'border-red-700 bg-red-700 text-white hover:bg-red-800',
  }

  const sizes: Record<Size, string> = {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-4 text-sm',
    lg: 'h-11 px-5 text-base',
  }

  return (
    <button className={cx(base, variants[variant], sizes[size], className)} {...rest}>
      {leftIcon}
      {children}
    </button>
  )
}
