import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Plot from 'react-plotly.js'
import { getJobResults } from '../api/client'
import type { JobResultsResponse } from '../api/types'
import Button from '../components/ui/Button'
import { Card, CardBody, CardHeader } from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import {
  downloadText,
  extractNexusSetsBlock,
  parseBestSchemeHeader,
  parseCharsetsFromNexusBlock,
  parseSchemeDataCsv,
  parseSubsetModelsFromIQtree,
  type SchemeRow,
} from '../utils/bestScheme'

export default function ResultsPage() {
  const { id } = useParams()
  const jobId = id ?? ''

  const [data, setData] = useState<JobResultsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const bestSchemeTxt = data?.best_scheme_txt ?? null
  const schemeDataCsv = data?.scheme_data_csv ?? null

  const [sortKey, setSortKey] = useState<keyof SchemeRow>('aicc')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

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
    if (!bestSchemeTxt) return null
    return extractNexusSetsBlock(bestSchemeTxt)
  }, [bestSchemeTxt])

  const bestHeader = useMemo(() => {
    if (!bestSchemeTxt) return null
    return parseBestSchemeHeader(bestSchemeTxt)
  }, [bestSchemeTxt])

  const subsetModels = useMemo(() => {
    if (!bestSchemeTxt) return []
    return parseSubsetModelsFromIQtree(bestSchemeTxt)
  }, [bestSchemeTxt])

  const charsets = useMemo(() => {
    if (!nexusBlock) return []
    return parseCharsetsFromNexusBlock(nexusBlock)
  }, [nexusBlock])

  const schemeRows = useMemo(() => {
    if (!schemeDataCsv) return []
    return parseSchemeDataCsv(schemeDataCsv)
  }, [schemeDataCsv])

  const sortedSchemes = useMemo(() => {
    const rows = [...schemeRows]
    const dir = sortDir === 'asc' ? 1 : -1
    rows.sort((a, b) => {
      const av = a[sortKey]
      const bv = b[sortKey]
      if (typeof av === 'number' && typeof bv === 'number') {
        if (!Number.isFinite(av) && !Number.isFinite(bv)) return 0
        if (!Number.isFinite(av)) return 1
        if (!Number.isFinite(bv)) return -1
        return (av - bv) * dir
      }
      return String(av).localeCompare(String(bv)) * dir
    })
    return rows.slice(0, 25)
  }, [schemeRows, sortKey, sortDir])

  function toggleSort(nextKey: typeof sortKey) {
    if (nextKey === sortKey) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(nextKey)
      setSortDir('asc')
    }
  }

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
    <div className="grid gap-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Results explorer</h1>
          <p className="mt-1 text-sm text-slate-600">Inspect outputs and export key files.</p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/">
            <Button variant="ghost">Dashboard</Button>
          </Link>
          <Link to={`/jobs/${jobId}/monitor`}>
            <Button variant="outline">Monitor</Button>
          </Link>
        </div>
      </div>

      {error && (
        <Card>
          <CardHeader title="Error" />
          <CardBody>
            <pre className="whitespace-pre-wrap text-sm text-red-700">{error}</pre>
          </CardBody>
        </Card>
      )}

      {!error && !data && (
        <Card>
          <CardHeader title="Loading" />
          <CardBody className="text-sm text-slate-600">Fetching results…</CardBody>
        </Card>
      )}

      {data && (
        <div className="grid gap-6">
          <Card>
            <CardHeader
              title={
                <span>
                  Job <span className="font-mono text-slate-900">{jobId}</span>
                </span>
              }
              right={
                <Badge tone={data.state === 'succeeded' ? 'teal' : data.state === 'failed' ? 'red' : 'slate'}>
                  {data.state}
                </Badge>
              }
            />
            <CardBody className="grid gap-3 text-sm text-slate-700">
              {data.cpus != null && data.cpus > 1 && (
                <div>
                  <span className="font-medium text-slate-900">Parallel run</span>: enabled
                  <span className="ml-1 text-slate-500">(CPUs={data.cpus})</span>
                </div>
              )}

              <div className="flex flex-wrap gap-2">
                <Button onClick={exportTxt} disabled={!data.best_scheme_txt}>
                  Export TXT
                </Button>
                <Button onClick={exportCsv} disabled={!data.scheme_data_csv} variant="secondary">
                  Export CSV
                </Button>
                <Button onClick={exportNexus} disabled={!nexusBlock} variant="outline">
                  Export Nexus
                </Button>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Best partition scheme" subtitle="Subset visualization and Nexus sets block" />
            <CardBody className="grid gap-4">
              {charsets.length === 0 ? (
                <p className="text-sm text-slate-600">Subset definitions not found in best_scheme.txt.</p>
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
                  <div className="text-sm font-semibold text-slate-900">Nexus sets block</div>
                  <pre className="mt-2 whitespace-pre-wrap rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-slate-800">
                    {nexusBlock}
                  </pre>
                </div>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Best models per partition" />
            <CardBody className="grid gap-4">
              {!data.best_scheme_txt ? (
                <p className="text-sm text-slate-600">No best_scheme.txt available yet.</p>
              ) : subsetModels.length === 0 ? (
                <p className="text-sm text-slate-600">Subset models not found in IQtree sets block.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-left text-sm">
                    <thead className="text-xs uppercase tracking-wide text-slate-500">
                      <tr>
                        <th className="py-2 pr-4">Subset</th>
                        <th className="py-2">Model</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {subsetModels.map((sm) => (
                        <tr key={sm.subset} className="hover:bg-slate-50">
                          <td className="py-2 pr-4 text-slate-900">{sm.subset}</td>
                          <td className="py-2 font-mono text-slate-700">{sm.model}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {bestHeader && (
                <div className="grid gap-1 text-sm text-slate-700">
                  {bestHeader.schemeName && (
                    <div>
                      <span className="font-medium text-slate-900">Best scheme</span>: {bestHeader.schemeName}
                    </div>
                  )}
                  {bestHeader.lnl != null && (
                    <div>
                      <span className="font-medium text-slate-900">lnL</span>: {bestHeader.lnl}
                    </div>
                  )}
                  {bestHeader.aic != null && (
                    <div>
                      <span className="font-medium text-slate-900">AIC</span>: {bestHeader.aic}
                    </div>
                  )}
                  {bestHeader.aicc != null && (
                    <div>
                      <span className="font-medium text-slate-900">AICc</span>: {bestHeader.aicc}
                    </div>
                  )}
                  {bestHeader.bic != null && (
                    <div>
                      <span className="font-medium text-slate-900">BIC</span>: {bestHeader.bic}
                    </div>
                  )}
                  {bestHeader.parameters != null && (
                    <div>
                      <span className="font-medium text-slate-900">Parameters</span>: {bestHeader.parameters}
                    </div>
                  )}
                  {bestHeader.sites != null && (
                    <div>
                      <span className="font-medium text-slate-900">Sites</span>: {bestHeader.sites}
                    </div>
                  )}
                  {bestHeader.subsets != null && (
                    <div>
                      <span className="font-medium text-slate-900">Subsets</span>: {bestHeader.subsets}
                    </div>
                  )}
                </div>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Model comparison plots" subtitle="AIC / AICc / BIC across schemes" />
            <CardBody>
              {schemeRows.length === 0 ? (
                <p className="text-sm text-slate-600">scheme_data.csv not available for this run.</p>
              ) : (
                <Plot
                  data={[
                    {
                      type: 'scatter',
                      mode: 'lines+markers',
                      name: 'AIC',
                      x: schemeRows.map((r) => r.name),
                      y: schemeRows.map((r) => r.aic),
                    },
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
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Top schemes" subtitle="Showing top 25 schemes (click headers to sort)" />
            <CardBody>
              {schemeRows.length === 0 ? (
                <p className="text-sm text-slate-600">scheme_data.csv not available for this run.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-left text-sm">
                    <thead className="text-xs uppercase tracking-wide text-slate-500">
                      <tr>
                        <th className="py-2 pr-2">
                          <button className="hover:text-slate-800" onClick={() => toggleSort('name')}>
                            Name
                          </button>
                        </th>
                        <th className="py-2 pr-2">
                          <button className="hover:text-slate-800" onClick={() => toggleSort('sites')}>
                            Sites
                          </button>
                        </th>
                        <th className="py-2 pr-2">
                          <button className="hover:text-slate-800" onClick={() => toggleSort('lnl')}>
                            lnL
                          </button>
                        </th>
                        <th className="py-2 pr-2">
                          <button className="hover:text-slate-800" onClick={() => toggleSort('parameters')}>
                            Params
                          </button>
                        </th>
                        <th className="py-2 pr-2">
                          <button className="hover:text-slate-800" onClick={() => toggleSort('subsets')}>
                            Subsets
                          </button>
                        </th>
                        <th className="py-2 pr-2">
                          <button className="hover:text-slate-800" onClick={() => toggleSort('aic')}>
                            AIC
                          </button>
                        </th>
                        <th className="py-2 pr-2">
                          <button className="hover:text-slate-800" onClick={() => toggleSort('aicc')}>
                            AICc
                          </button>
                        </th>
                        <th className="py-2">
                          <button className="hover:text-slate-800" onClick={() => toggleSort('bic')}>
                            BIC
                          </button>
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {sortedSchemes.map((r) => (
                        <tr key={r.name} className="hover:bg-slate-50">
                          <td className="py-2 pr-2 font-mono text-slate-900">{r.name}</td>
                          <td className="py-2 pr-2 text-slate-700">{r.sites}</td>
                          <td className="py-2 pr-2 text-slate-700">
                            {Number.isFinite(r.lnl) ? r.lnl.toFixed(2) : String(r.lnl)}
                          </td>
                          <td className="py-2 pr-2 text-slate-700">{r.parameters}</td>
                          <td className="py-2 pr-2 text-slate-700">{r.subsets}</td>
                          <td className="py-2 pr-2 text-slate-700">
                            {Number.isFinite(r.aic) ? r.aic.toFixed(2) : String(r.aic)}
                          </td>
                          <td className="py-2 pr-2 text-slate-700">
                            {Number.isFinite(r.aicc) ? r.aicc.toFixed(2) : String(r.aicc)}
                          </td>
                          <td className="py-2 text-slate-700">
                            {Number.isFinite(r.bic) ? r.bic.toFixed(2) : String(r.bic)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Best scheme text" />
            <CardBody>
              <pre className="max-h-[520px] overflow-auto whitespace-pre-wrap rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-slate-800">
                {data.best_scheme_txt ?? 'No output yet.'}
              </pre>
            </CardBody>
          </Card>
        </div>
      )}
    </div>
  )
}
