import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getJobStatus, jobLogWebSocketUrl, listJobs } from '../api/client'
import type { JobState } from '../api/types'

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
  const [avgSeconds, setAvgSeconds] = useState<number | null>(null)

  useEffect(() => {
    let cancelled = false

    async function refreshStatus() {
      try {
        const s = await getJobStatus(jobId)
        if (cancelled) return
        setState(s.state)
        const created = Date.parse(s.created_at)
        if (Number.isFinite(created)) setCreatedAt(created)
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
    return (Date.now() - createdAt) / 1000
  }, [createdAt])

  const eta = useMemo(() => {
    if (elapsed == null || avgSeconds == null) return null
    return Math.max(0, avgSeconds - elapsed)
  }, [elapsed, avgSeconds])

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
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <h1>Execution monitor</h1>
        <Link to="/">Dashboard</Link>
      </header>

      {error && <p style={{ whiteSpace: 'pre-wrap' }}>{error}</p>}

      <div style={{ display: 'grid', gap: 8 }}>
        <div>
          <strong>Job</strong>: <span style={{ fontFamily: 'monospace' }}>{jobId}</span>
        </div>
        <div>
          <strong>Status</strong>: {state}
        </div>
        <div>
          <strong>Elapsed</strong>: {elapsed == null ? '—' : formatSeconds(elapsed)}
        </div>
        <div>
          <strong>Estimated completion time</strong>: {eta == null ? '—' : formatSeconds(eta)} remaining
        </div>
        <div>
          <progress />
        </div>
        <div>
          <h2>Live logs</h2>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{log || 'Waiting for logs…'}</pre>
        </div>
        <div>
          <Link to={`/jobs/${jobId}/results`}>View results</Link>
        </div>
      </div>
    </div>
  )
}
