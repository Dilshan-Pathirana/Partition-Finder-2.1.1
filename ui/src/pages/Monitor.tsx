import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getJobStatus, jobLogWebSocketUrl, listJobs, stopJob } from '../api/client'
import type { JobState } from '../api/types'
import Button from '../components/ui/Button'
import { Card, CardBody, CardHeader } from '../components/ui/Card'
import Badge from '../components/ui/Badge'

function formatSeconds(s: number): string {
  if (!Number.isFinite(s) || s < 0) return '—'
  if (s < 60) return `${Math.round(s)}s`
  const m = Math.floor(s / 60)
  const r = Math.round(s % 60)
  return `${m}m ${r}s`
}

export default function MonitorPage() {
  const { id } = useParams()
  const jobId = id ?? ''

  const [state, setState] = useState<JobState>('queued')
  const [error, setError] = useState<string | null>(null)
  const [log, setLog] = useState('')
  const [createdAt, setCreatedAt] = useState<number | null>(null)
  const [updatedAt, setUpdatedAt] = useState<number | null>(null)
  const [nowMs, setNowMs] = useState(() => Date.now())
  const [cpus, setCpus] = useState<number | null>(null)
  const [avgSeconds, setAvgSeconds] = useState<number | null>(null)
  const [stopping, setStopping] = useState(false)

  useEffect(() => {
    const t = window.setInterval(() => setNowMs(Date.now()), 1000)
    return () => window.clearInterval(t)
  }, [])

  useEffect(() => {
    let cancelled = false

    async function refreshStatus() {
      try {
        const s = await getJobStatus(jobId)
        if (cancelled) return
        setState(s.state)
        setCpus(s.cpus ?? null)
        const created = Date.parse(s.created_at)
        if (Number.isFinite(created)) setCreatedAt(created)
        const updated = Date.parse(s.updated_at)
        if (Number.isFinite(updated)) setUpdatedAt(updated)
        setError(null)
      } catch (e) {
        if (cancelled) return
        setError(e instanceof Error ? e.message : String(e))
      }
    }

    void refreshStatus()
    const t = window.setInterval(() => void refreshStatus(), 1000)
    return () => {
      cancelled = true
      window.clearInterval(t)
    }
  }, [jobId])

  async function onStop() {
    if (!jobId) return
    if (!confirm(`Stop job ${jobId}?`)) return
    setStopping(true)
    setError(null)
    try {
      await stopJob(jobId)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setStopping(false)
    }
  }

  useEffect(() => {
    let cancelled = false

    async function loadAvg() {
      try {
        const jobs = await listJobs(50)
        if (cancelled) return
        const durations: number[] = []
        for (const j of jobs) {
          if (j.state !== 'succeeded' && j.state !== 'failed') continue
          const c = Date.parse(j.created_at)
          const u = Date.parse(j.updated_at)
          if (Number.isFinite(c) && Number.isFinite(u) && u >= c) durations.push((u - c) / 1000)
        }
        if (durations.length > 0) {
          setAvgSeconds(durations.reduce((a, b) => a + b, 0) / durations.length)
        }
      } catch {
        // ignore
      }
    }

    void loadAvg()
    return () => {
      cancelled = true
    }
  }, [])

  const elapsed = useMemo(() => {
    if (!createdAt) return null
    if ((state === 'succeeded' || state === 'failed') && updatedAt && updatedAt >= createdAt) {
      return (updatedAt - createdAt) / 1000
    }
    return (nowMs - createdAt) / 1000
  }, [createdAt, nowMs, state, updatedAt])

  const eta = useMemo(() => {
    if (state === 'succeeded' || state === 'failed') return 0
    if (elapsed == null || avgSeconds == null) return null
    return Math.max(0, avgSeconds - elapsed)
  }, [elapsed, avgSeconds, state])

  const progressValue = useMemo(() => {
    if (state === 'succeeded' || state === 'failed') return 1
    if (elapsed == null || avgSeconds == null || avgSeconds <= 0) return null
    return Math.max(0, Math.min(0.98, elapsed / avgSeconds))
  }, [elapsed, avgSeconds, state])

  useEffect(() => {
    if (!jobId) return

    const ws = new WebSocket(jobLogWebSocketUrl(jobId))
    ws.onmessage = (ev) => {
      setLog((prev) => prev + String(ev.data))
    }
    ws.onerror = () => {
      setError('WebSocket error while streaming logs')
    }

    return () => {
      ws.close()
    }
  }, [jobId])

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Execution monitor</h1>
          <p className="mt-1 text-sm text-slate-600">Live status, ETA, and streaming logs.</p>
        </div>
        <Link to="/">
          <Button variant="ghost">Dashboard</Button>
        </Link>
      </div>

      {error && (
        <Card>
          <CardHeader title="Error" />
          <CardBody>
            <pre className="whitespace-pre-wrap text-sm text-red-700">{error}</pre>
          </CardBody>
        </Card>
      )}

      <Card>
        <CardHeader
          title={
            <span>
              Job <span className="font-mono text-slate-900">{jobId}</span>
            </span>
          }
          right={
            <div className="flex items-center gap-2">
              <Link to={`/jobs/${jobId}/results`}>
                <Button size="sm" variant="outline">
                  View results
                </Button>
              </Link>
              <Button
                size="sm"
                variant="danger"
                onClick={() => void onStop()}
                disabled={stopping || state !== 'running'}
              >
                {stopping ? 'Stopping…' : 'Stop job'}
              </Button>
            </div>
          }
        />
        <CardBody className="grid gap-3 text-sm">
          <div className="flex flex-wrap items-center gap-3">
            <div className="text-slate-700">
              <span className="font-medium text-slate-900">Status</span>:{' '}
              <Badge
                tone={
                  state === 'succeeded' ? 'teal' : state === 'failed' ? 'red' : 'slate'
                }
              >
                {state}
              </Badge>
            </div>
            {cpus != null && cpus > 1 && (
              <div className="text-slate-700">
                <span className="font-medium text-slate-900">Parallel run</span>: enabled
                <span className="ml-1 text-slate-500">(CPUs={cpus})</span>
              </div>
            )}
          </div>

          <div className="grid gap-2 sm:grid-cols-2">
            <div className="text-slate-700">
              <span className="font-medium text-slate-900">Elapsed</span>:{' '}
              {elapsed == null ? '—' : formatSeconds(elapsed)}
            </div>
            <div className="text-slate-700">
              <span className="font-medium text-slate-900">ETA</span>:{' '}
              {eta == null ? '—' : `${formatSeconds(eta)} remaining`}
            </div>
          </div>

          <div>
            {progressValue == null && state === 'running' ? (
              <div className="h-2 w-full overflow-hidden rounded bg-slate-200">
                <div className="h-full w-1/3 animate-pulse bg-slate-500" />
              </div>
            ) : (
              <progress max={1} value={progressValue ?? undefined} className="h-2 w-full" />
            )}
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Live logs" subtitle="Streaming output as the job runs" />
        <CardBody>
          <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-slate-800">
            {log || 'Waiting for logs…'}
          </pre>
        </CardBody>
      </Card>
    </div>
  )
}
