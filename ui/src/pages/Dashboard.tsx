import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { deleteJob, listJobs } from '../api/client'
import type { JobStatusResponse } from '../api/types'

export default function DashboardPage() {
  const [jobs, setJobs] = useState<JobStatusResponse[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function refresh() {
    setError(null)
    setBusy(true)
    try {
      setJobs(await listJobs(50))
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    void refresh()
  }, [])

  const completedDurations = useMemo(() => {
    const durations: number[] = []
    for (const j of jobs) {
      if (j.state !== 'succeeded' && j.state !== 'failed') continue
      const created = Date.parse(j.created_at)
      const updated = Date.parse(j.updated_at)
      if (Number.isFinite(created) && Number.isFinite(updated) && updated >= created) {
        durations.push((updated - created) / 1000)
      }
    }
    return durations
  }, [jobs])

  const avgSeconds = useMemo(() => {
    if (completedDurations.length === 0) return null
    return completedDurations.reduce((a, b) => a + b, 0) / completedDurations.length
  }, [completedDurations])

  async function onDelete(id: string) {
    if (!confirm(`Delete job ${id}?`)) return
    setError(null)
    try {
      await deleteJob(id)
      await refresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  return (
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <h1>PartitionFinder</h1>
        <Link to="/new/upload">New analysis</Link>
      </header>

      <section>
        <h2>Project dashboard</h2>
        {avgSeconds != null && (
          <p>
            Typical runtime estimate: ~{Math.max(1, Math.round(avgSeconds))}s (based on previous
            completed jobs)
          </p>
        )}
        <button onClick={refresh} disabled={busy}>
          Refresh
        </button>
        {error && <p style={{ whiteSpace: 'pre-wrap' }}>{error}</p>}

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', textAlign: 'left' }}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Status</th>
                <th>Datatype</th>
                <th>Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {jobs.length === 0 ? (
                <tr>
                  <td colSpan={5}>No analyses yet.</td>
                </tr>
              ) : (
                jobs.map((j) => (
                  <tr key={j.id}>
                    <td style={{ fontFamily: 'monospace' }}>{j.id.slice(0, 8)}</td>
                    <td>{j.state}</td>
                    <td>{j.datatype ?? '-'}</td>
                    <td>{j.updated_at}</td>
                    <td>
                      <Link to={`/jobs/${j.id}/monitor`}>Monitor</Link>
                      {' | '}
                      <Link to={`/jobs/${j.id}/results`}>Results</Link>
                      {' | '}
                      <button onClick={() => void onDelete(j.id)} disabled={j.state === 'running'}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
