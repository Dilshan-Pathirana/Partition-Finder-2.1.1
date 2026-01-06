import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { submitJob } from '../api/client'
import type { JobRequest } from '../api/types'
import WorkflowStepper from '../components/layout/WorkflowStepper'
import Button from '../components/ui/Button'
import { Card, CardBody, CardHeader } from '../components/ui/Card'

export default function RunPage() {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  const req = useMemo((): JobRequest | null => {
    const folder = sessionStorage.getItem('pf.new.folder') ?? ''
    const datatypeRaw = sessionStorage.getItem('pf.new.datatype')
    const datatype: JobRequest['datatype'] =
      datatypeRaw === 'DNA' || datatypeRaw === 'protein' || datatypeRaw === 'morphology'
        ? datatypeRaw
        : 'DNA'
    const overridesRaw = sessionStorage.getItem('pf.new.overrides')
    const overrides = overridesRaw ? (JSON.parse(overridesRaw) as Record<string, string>) : {}
    const cpusRaw = sessionStorage.getItem('pf.new.cpus')
    const cpus = cpusRaw ? Number(cpusRaw) : 1

    if (!folder.trim()) return null

    return {
      folder,
      datatype,
      cpus: Number.isFinite(cpus) && cpus >= 1 ? Math.floor(cpus) : 1,
      args: [],
      copy_input: true,
      overrides,
    }
  }, [])

  useEffect(() => {
    let cancelled = false

    async function run() {
      if (!req) {
        setError('Missing setup. Start from Data Upload.')
        return
      }

      setError(null)

      try {
        const { id } = await submitJob(req)
        if (cancelled) return
        navigate(`/jobs/${id}/monitor`, { replace: true })
      } catch (e) {
        if (cancelled) return
        setError(e instanceof Error ? e.message : String(e))
      }
    }

    void run()
    return () => {
      cancelled = true
    }
  }, [req, navigate])

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">New analysis</h1>
          <p className="mt-1 text-sm text-slate-600">Submitting your job to the backend.</p>
        </div>
        <Link to="/new/config">
          <Button variant="ghost">Back</Button>
        </Link>
      </div>

      <WorkflowStepper active="run" />

      {error && (
        <Card>
          <CardHeader title="Error" />
          <CardBody>
            <pre className="whitespace-pre-wrap text-sm text-red-700">{error}</pre>
          </CardBody>
        </Card>
      )}

      {!error && (
        <Card>
          <CardHeader title="Submitting" subtitle="You will be redirected to the live monitor" />
          <CardBody className="grid gap-3 text-sm text-slate-700">
            <div>
              <span className="font-medium text-slate-900">Status</span>: Submitting job…
            </div>
            <div>
              <progress className="h-2 w-full" />
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
