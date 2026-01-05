import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getJobStatus, submitJob } from '../api/client'
import type { JobRequest, JobState } from '../api/types'

function formatSeconds(s: number): string {
  if (!Number.isFinite(s) || s < 0) return '—'
  if (s < 60) return `${Math.round(s)}s`
  const m = Math.floor(s / 60)
  const r = Math.round(s % 60)
  return `${m}m ${r}s`
}

export default function RunPage() {
  const navigate = useNavigate()
  const [jobId, setJobId] = useState<string | null>(null)
  const [state, setState] = useState<JobState | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [startedAt, setStartedAt] = useState<number | null>(null)

  const req = useMemo((): JobRequest | null => {
    const folder = sessionStorage.getItem('pf.new.folder') ?? ''
    const datatype = (sessionStorage.getItem('pf.new.datatype') as any) ?? 'DNA'
    const overridesRaw = sessionStorage.getItem('pf.new.overrides')
    const overrides = overridesRaw ? (JSON.parse(overridesRaw) as Record<string, string>) : {}

    if (!folder.trim()) return null

    return {
      folder,
      datatype,
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
      setStartedAt(Date.now())

      try {
        const { id } = await submitJob(req)
        if (cancelled) return
        setJobId(id)
        setState('queued')

        // Poll until running/succeeded/failed.
        while (!cancelled) {
          const s = await getJobStatus(id)
          if (cancelled) return
          setState(s.state)
          if (s.state === 'succeeded' || s.state === 'failed') break
          await new Promise((r) => setTimeout(r, 600))
        }
      } catch (e) {
        if (cancelled) return
        setError(e instanceof Error ? e.message : String(e))
      }
    }

    void run()
    return () => {
      cancelled = true
    }
  }, [req])

  const elapsed = startedAt ? (Date.now() - startedAt) / 1000 : null

  function goMonitor() {
    if (jobId) navigate(`/jobs/${jobId}/monitor`)
  }

  function goResults() {
    if (jobId) navigate(`/jobs/${jobId}/results`)
  }

  return (
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <h1>New analysis</h1>
        <Link to="/new/config">Back</Link>
      </header>

      <h2>Run</h2>
      <p>Step 3 of 4 — Upload → Configure → Run → Interpret</p>

      {error && <p style={{ whiteSpace: 'pre-wrap' }}>{error}</p>}

      {!error && (
        <div style={{ display: 'grid', gap: 8 }}>
          <div>
            <strong>Job</strong>: {jobId ? jobId : 'Submitting…'}
          </div>
          <div>
            <strong>Status</strong>: {state ?? '…'}
          </div>
          <div>
            <strong>Elapsed</strong>: {elapsed == null ? '—' : formatSeconds(elapsed)}
          </div>
          <div>
            <progress />
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={goMonitor} disabled={!jobId}>
              Open live monitor
            </button>
            <button onClick={goResults} disabled={!jobId || (state !== 'succeeded' && state !== 'failed')}>
              View results
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
