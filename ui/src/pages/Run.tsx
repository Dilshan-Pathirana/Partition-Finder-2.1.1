import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { submitJob } from '../api/client'
import type { JobRequest } from '../api/types'

export default function RunPage() {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  const req = useMemo((): JobRequest | null => {
    const folder = sessionStorage.getItem('pf.new.folder') ?? ''
    const datatype = (sessionStorage.getItem('pf.new.datatype') as any) ?? 'DNA'
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
  }, [req])

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
            <strong>Status</strong>: Submitting job…
          </div>
          <div>
            <progress />
          </div>
          <p>You will be redirected to the live monitor.</p>
        </div>
      )}
    </div>
  )
}
