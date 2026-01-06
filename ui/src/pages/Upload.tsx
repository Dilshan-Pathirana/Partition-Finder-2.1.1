import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Plot from 'react-plotly.js'
import { browseFolder, previewFolder } from '../api/client'
import type { FolderPreviewResponse } from '../api/types'
import WorkflowStepper from '../components/layout/WorkflowStepper'
import Button from '../components/ui/Button'
import { Card, CardBody, CardHeader } from '../components/ui/Card'
import { Input, Label } from '../components/ui/Form'
import Badge from '../components/ui/Badge'

export interface UploadState {
  folder: string
  alignmentPreview: string | null
}

export default function UploadPage(props: {
  state: UploadState
  onChange: (next: UploadState) => void
}) {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [preview, setPreview] = useState<FolderPreviewResponse | null>(null)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [pickingFolder, setPickingFolder] = useState(false)

  async function onPickAlignment(file: File | null) {
    setError(null)
    if (!file) {
      props.onChange({ ...props.state, alignmentPreview: null })
      return
    }

    try {
      const text = await file.text()
      props.onChange({ ...props.state, alignmentPreview: text.split(/\r?\n/).slice(0, 40).join('\n') })
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  function next() {
    setError(null)
    if (!props.state.folder.trim()) {
      setError('Please enter a folder path that contains partition_finder.cfg')
      return
    }
    navigate('/new/config')
  }

  async function validateFolder(folderArg?: string) {
    setPreviewError(null)
    setPreview(null)
    const folder = (folderArg ?? props.state.folder).trim()
    if (!folder) {
      setPreviewError('Please enter a folder path first.')
      return
    }
    setBusy(true)
    try {
      setPreview(await previewFolder({ folder }))
    } catch (e) {
      setPreviewError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }

  async function chooseFolder() {
    setError(null)
    setPreviewError(null)
    setPickingFolder(true)
    try {
      const res = await browseFolder()
      if (res.folder) {
        props.onChange({ ...props.state, folder: res.folder })
        await validateFolder(res.folder)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setPickingFolder(false)
    }
  }

  const dataBlockLengths = useMemo(() => {
    const blocks = preview?.data_blocks ?? []
    const xs: string[] = []
    const ys: number[] = []
    for (const b of blocks) {
      xs.push(b.name)
      ys.push(typeof b.length === 'number' && Number.isFinite(b.length) ? b.length : 0)
    }
    return { xs, ys }
  }, [preview])

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">New analysis</h1>
          <p className="mt-1 text-sm text-slate-600">Provide the input folder and validate it.</p>
        </div>
        <Link to="/">
          <Button variant="ghost">Back to dashboard</Button>
        </Link>
      </div>

      <WorkflowStepper active="upload" />

      <Card>
        <CardHeader title="Input folder" subtitle="Must contain partition_finder.cfg" />
        <CardBody className="grid gap-4">
          <div className="grid gap-2">
            <Label title="Folder path" hint="Choose a folder or paste a path. Example: E:\\path\\to\\analysis_folder">
              <Input
                type="text"
                value={props.state.folder}
                onChange={(e) => props.onChange({ ...props.state, folder: e.target.value })}
                placeholder="E:\\path\\to\\analysis_folder"
              />
            </Label>
            <div>
              <Button variant="secondary" onClick={() => void chooseFolder()} disabled={pickingFolder}>
                {pickingFolder ? 'Opening…' : 'Choose folder'}
              </Button>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button onClick={() => void validateFolder()} disabled={busy}>
              {busy ? 'Validating…' : 'Validate folder'}
            </Button>
            {preview && <Badge tone="teal">OK</Badge>}
          </div>

          {previewError && <pre className="whitespace-pre-wrap text-sm text-red-700">{previewError}</pre>}
        </CardBody>
      </Card>

      {preview && (
        <Card>
          <CardHeader
            title="Folder preview"
            subtitle="What PartitionFinder will read from this folder"
          />
          <CardBody className="grid gap-6">
            <div className="grid gap-2 text-sm">
              <div>
                <span className="font-medium text-slate-900">Config</span>:{' '}
                <span className="text-slate-700">{preview.cfg_file}</span>
              </div>
              <div>
                <span className="font-medium text-slate-900">Alignment</span>:{' '}
                <span className="text-slate-700">{preview.alignment ?? '—'}</span>
              </div>
              <div>
                <span className="font-medium text-slate-900">Data blocks</span>:{' '}
                <span className="text-slate-700">{preview.data_blocks.length}</span>
              </div>
            </div>

            <div>
              <div className="text-sm font-semibold text-slate-900">Data block visualization</div>
              <div className="mt-2">
                {preview.data_blocks.length === 0 ? (
                  <p className="text-sm text-slate-600">No [data_blocks] found in the config.</p>
                ) : (
                  <Plot
                    data={[
                      {
                        type: 'bar',
                        x: dataBlockLengths.xs,
                        y: dataBlockLengths.ys,
                      },
                    ]}
                    layout={{
                      title: { text: 'Block lengths (sites)' },
                      xaxis: { title: { text: 'Block' } },
                      yaxis: { title: { text: 'Sites' } },
                      margin: { t: 40, r: 10, b: 80, l: 60 },
                    }}
                    style={{ width: '100%', height: 320 }}
                    config={{ displayModeBar: false }}
                  />
                )}
              </div>

              {preview.data_blocks.length > 0 && (
                <div className="mt-3 overflow-x-auto">
                  <table className="min-w-full text-left text-sm">
                    <thead className="text-xs uppercase tracking-wide text-slate-500">
                      <tr>
                        <th className="py-2 pr-4">Block</th>
                        <th className="py-2 pr-4">Range</th>
                        <th className="py-2">Sites</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {preview.data_blocks.map((b) => (
                        <tr key={b.name} className="hover:bg-slate-50">
                          <td className="py-2 pr-4 text-slate-900">{b.name}</td>
                          <td className="py-2 pr-4 font-mono text-slate-700">{b.range}</td>
                          <td className="py-2 text-slate-700">{b.length ?? '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </CardBody>
        </Card>
      )}

      <Card>
        <CardHeader title="Alignment preview (optional)" subtitle="Loads locally in your browser" />
        <CardBody className="grid gap-4">
          <input
            type="file"
            accept=".phy,.phylip,.nex,.nexus,.fasta,.fa,.fas,.txt"
            onChange={(e) => void onPickAlignment(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-slate-700 file:mr-3 file:rounded-md file:border file:border-slate-300 file:bg-white file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-900 hover:file:bg-slate-50"
          />

          {error && <pre className="whitespace-pre-wrap text-sm text-red-700">{error}</pre>}

          {props.state.alignmentPreview && (
            <pre className="max-h-72 overflow-auto rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-slate-800">
              {props.state.alignmentPreview}
            </pre>
          )}
        </CardBody>
      </Card>

      <div className="flex items-center justify-end gap-2">
        <Button onClick={next}>Continue</Button>
      </div>
    </div>
  )
}
