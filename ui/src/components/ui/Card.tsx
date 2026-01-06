import type { HTMLAttributes, ReactNode } from 'react'

function cx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(' ')
}

export function Card(props: HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props
  return (
    <div
      className={cx(
        'rounded-xl border border-slate-200 bg-white shadow-sm shadow-slate-200/50',
        className,
      )}
      {...rest}
    />
  )
}

export function CardHeader(props: { title: ReactNode; subtitle?: ReactNode; right?: ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-100 px-5 py-4">
      <div className="min-w-0">
        <div className="text-base font-semibold text-slate-900">{props.title}</div>
        {props.subtitle && <div className="mt-1 text-sm text-slate-600">{props.subtitle}</div>}
      </div>
      {props.right ? <div className="shrink-0">{props.right}</div> : null}
    </div>
  )
}

export function CardBody(props: HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props
  return <div className={cx('px-5 py-4', className)} {...rest} />
}
