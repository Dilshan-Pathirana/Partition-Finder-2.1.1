import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Plot from 'react-plotly.js'
import { getJobResults } from '../api/client'
import type { JobResultsResponse } from '../api/types'
import {
  downloadText,
  extractNexusSetsBlock,
  parseCharsetsFromNexusBlock,
  parseSchemeDataCsv,
} from '../utils/bestScheme'

export default function ResultsPage() {
  const { id } = useParams()
  const jobId = id ?? ''

  const [data, setData] = useState<JobResultsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setError(null)
      try {
        const r = await getJobResults(jobId)
        if (cancelled) return
        setData(r)
      } catch (e) {
        if (cancelled) return
        setError(e instanceof Error ? e.message : String(e))
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [jobId])

  const nexusBlock = useMemo(() => {
    if (!data?.best_scheme_txt) return null
    return extractNexusSetsBlock(data.best_scheme_txt)
  }, [data?.best_scheme_txt])

  const charsets = useMemo(() => {
    if (!nexusBlock) return []
    return parseCharsetsFromNexusBlock(nexusBlock)
  }, [nexusBlock])

  const schemeRows = useMemo(() => {
    if (!data?.scheme_data_csv) return []
    return parseSchemeDataCsv(data.scheme_data_csv)
  }, [data?.scheme_data_csv])

  function exportTxt() {
    if (!data?.best_scheme_txt) return
    downloadText(`best_scheme_${jobId}.txt`, data.best_scheme_txt)
  }

  function exportCsv() {
    if (!data?.scheme_data_csv) return
    downloadText(`scheme_data_${jobId}.csv`, data.scheme_data_csv)
  }

  function exportNexus() {
    if (!nexusBlock) return
    const content = `#nexus\n\n${nexusBlock}\n`
    downloadText(`best_scheme_sets_${jobId}.nex`, content)
  }

  return (
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <h1>Results explorer</h1>
        <Link to="/">Dashboard</Link>
      </header>

      {error && <p style={{ whiteSpace: 'pre-wrap' }}>{error}</p>}
      {!error && !data && <p>Loading…</p>}

      {data && (
        <div style={{ display: 'grid', gap: 12 }}>
          <div>
            <strong>Job</strong>: <span style={{ fontFamily: 'monospace' }}>{jobId}</span>
          </div>
          <div>
            <strong>Status</strong>: {data.state}
          </div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button onClick={exportTxt} disabled={!data.best_scheme_txt}>
              Export TXT
            </button>
            <button onClick={exportCsv} disabled={!data.scheme_data_csv}>
              Export CSV
            </button>
            <button onClick={exportNexus} disabled={!nexusBlock}>
              Export Nexus
            </button>
          </div>

          <section>
            <h2>Best partition scheme visualization</h2>
            {charsets.length === 0 ? (
              <p>Subset definitions not found in best_scheme.txt.</p>
            ) : (
              <Plot
                data={[
                  {
                    type: 'bar',
                    x: charsets.map((c) => c.subset),
                    y: charsets.map((c) => c.length ?? 0),
                  },
                ]}
                layout={{
                  title: { text: 'Subset lengths' },
                  xaxis: { title: { text: 'Subset' } },
                  yaxis: { title: { text: 'Sites' } },
                  margin: { t: 40, r: 10, b: 50, l: 50 },
                }}
                style={{ width: '100%', height: 320 }}
                config={{ displayModeBar: false }}
              />
            )}

            {nexusBlock && (
              <div>
                <h3>Nexus sets block</h3>
                <pre style={{ whiteSpace: 'pre-wrap' }}>{nexusBlock}</pre>
              </div>
            )}
          </section>

          <section>
            <h2>Model comparison plots</h2>
            {schemeRows.length === 0 ? (
              <p>scheme_data.csv not available for this run.</p>
            ) : (
              <Plot
                data={[
                  {
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'AICc',
                    x: schemeRows.map((r) => r.name),
                    y: schemeRows.map((r) => r.aicc),
                  },
                  {
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'BIC',
                    x: schemeRows.map((r) => r.name),
                    y: schemeRows.map((r) => r.bic),
                  },
                ]}
                layout={{
                  title: { text: 'Scheme scores' },
                  xaxis: { title: { text: 'Scheme' } },
                  yaxis: { title: { text: 'Score' } },
                  margin: { t: 40, r: 10, b: 80, l: 60 },
                }}
                style={{ width: '100%', height: 360 }}
                config={{ displayModeBar: false }}
              />
            )}
          </section>

          <section>
            <h2>Best scheme text</h2>
            <pre style={{ whiteSpace: 'pre-wrap' }}>{data.best_scheme_txt ?? 'No output yet.'}</pre>
          </section>

          <div>
            <Link to={`/jobs/${jobId}/monitor`}>Back to monitor</Link>
          </div>
        </div>
      )}
    </div>
  )
}
