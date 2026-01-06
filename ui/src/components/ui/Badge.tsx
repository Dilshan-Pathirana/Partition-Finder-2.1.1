import type { HTMLAttributes } from 'react'

function cx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(' ')
}

export default function Badge(
  props: HTMLAttributes<HTMLSpanElement> & { tone?: 'slate' | 'teal' | 'red' },
) {
  const { tone = 'slate', className, ...rest } = props

  const tones: Record<string, string> = {
    slate: 'border-slate-200 bg-slate-50 text-slate-700',
    teal: 'border-teal-200 bg-teal-50 text-teal-800',
    red: 'border-red-200 bg-red-50 text-red-800',
  }

  return (
    <span
      className={cx(
        'inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium',
        tones[tone],
        className,
      )}
      {...rest}
    />
  )
}
