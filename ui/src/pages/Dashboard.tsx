import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { deleteJob, listJobs } from '../api/client'
import type { JobStatusResponse } from '../api/types'
import Button from '../components/ui/Button'
import { Card, CardBody, CardHeader } from '../components/ui/Card'
import Badge from '../components/ui/Badge'

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
    <div className="grid gap-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Project dashboard</h1>
          <p className="mt-1 text-sm text-slate-600">
            Create and monitor PartitionFinder analyses.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/new/upload">
            <Button>New analysis</Button>
          </Link>
          <Button variant="secondary" onClick={refresh} disabled={busy}>
            {busy ? 'Refreshing…' : 'Refresh'}
          </Button>
        </div>
      </div>

      {avgSeconds != null && (
        <Card>
          <CardBody className="text-sm text-slate-700">
            Typical runtime estimate:{' '}
            <span className="font-medium text-slate-900">
              ~{Math.max(1, Math.round(avgSeconds))}s
            </span>{' '}
            <span className="text-slate-500">(based on previous completed jobs)</span>
          </CardBody>
        </Card>
      )}

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
          title="Analyses"
          subtitle={jobs.length === 0 ? 'No analyses yet.' : `Showing up to ${jobs.length} jobs.`}
        />
        <CardBody>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="py-2 pr-4">ID</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">Datatype</th>
                  <th className="py-2 pr-4">Updated</th>
                  <th className="py-2">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {jobs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-6 text-slate-500">
                      No analyses yet.
                    </td>
                  </tr>
                ) : (
                  jobs.map((j) => (
                    <tr key={j.id} className="hover:bg-slate-50">
                      <td className="py-3 pr-4 font-mono text-slate-900">{j.id.slice(0, 8)}</td>
                      <td className="py-3 pr-4">
                        <Badge
                          tone={
                            j.state === 'succeeded'
                              ? 'teal'
                              : j.state === 'failed'
                                ? 'red'
                                : 'slate'
                          }
                        >
                          {j.state}
                        </Badge>
                      </td>
                      <td className="py-3 pr-4 text-slate-700">{j.datatype ?? '—'}</td>
                      <td className="py-3 pr-4 text-slate-600">{j.updated_at}</td>
                      <td className="py-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <Link to={`/jobs/${j.id}/monitor`}>
                            <Button size="sm" variant="outline">
                              Monitor
                            </Button>
                          </Link>
                          <Link to={`/jobs/${j.id}/results`}>
                            <Button size="sm" variant="outline">
                              Results
                            </Button>
                          </Link>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => void onDelete(j.id)}
                            disabled={j.state === 'running'}
                          >
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
