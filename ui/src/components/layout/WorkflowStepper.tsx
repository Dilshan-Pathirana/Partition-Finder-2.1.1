type Step = {
  key: 'upload' | 'configure' | 'run' | 'interpret'
  label: string
}

const steps: Step[] = [
  { key: 'upload', label: 'Upload' },
  { key: 'configure', label: 'Configure' },
  { key: 'run', label: 'Run' },
  { key: 'interpret', label: 'Interpret' },
]

function cx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(' ')
}

export default function WorkflowStepper(props: { active: Step['key'] }) {
  const activeIndex = steps.findIndex((s) => s.key === props.active)

  return (
    <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm shadow-slate-200/50">
      <div className="flex flex-wrap items-center gap-2">
        {steps.map((s, i) => {
          const done = i < activeIndex
          const active = i === activeIndex

          return (
            <div key={s.key} className="flex items-center gap-2">
              <div
                className={cx(
                  'flex h-7 w-7 items-center justify-center rounded-full border text-sm font-semibold',
                  done && 'border-teal-600 bg-teal-600 text-white',
                  active && 'border-teal-700 bg-teal-50 text-teal-800',
                  !done && !active && 'border-slate-300 bg-white text-slate-600',
                )}
              >
                {i + 1}
              </div>
              <div
                className={cx(
                  'text-sm font-medium',
                  done && 'text-slate-600',
                  active && 'text-slate-900',
                  !done && !active && 'text-slate-600',
                )}
              >
                {s.label}
              </div>
              {i < steps.length - 1 && (
                <div className="mx-1 hidden h-px w-8 bg-slate-200 sm:block" />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
