import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Plot from 'react-plotly.js'
import { previewFolder } from '../api/client'
import type { FolderPreviewResponse } from '../api/types'

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

  async function validateFolder() {
    setPreviewError(null)
    setPreview(null)
    const folder = props.state.folder.trim()
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
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <h1>New analysis</h1>
        <Link to="/">Back to dashboard</Link>
      </header>

      <h2>Data upload</h2>
      <p>Step 1 of 4 — Upload → Configure → Run → Interpret</p>

      <label style={{ display: 'block', marginTop: 12 }}>
        Input folder path (must contain a .cfg file)
        <input
          type="text"
          value={props.state.folder}
          onChange={(e) => props.onChange({ ...props.state, folder: e.target.value })}
          style={{ width: '100%' }}
          placeholder="E:\\path\\to\\analysis_folder"
        />
      </label>

      <div style={{ marginTop: 8, display: 'flex', gap: 8, alignItems: 'center' }}>
        <button onClick={() => void validateFolder()} disabled={busy}>
          {busy ? 'Validating…' : 'Validate folder'}
        </button>
        {preview && <span>OK</span>}
      </div>

      {previewError && <p style={{ whiteSpace: 'pre-wrap' }}>{previewError}</p>}

      {preview && (
        <div style={{ marginTop: 12 }}>
          <h3>Folder preview</h3>
          <div style={{ display: 'grid', gap: 6 }}>
            <div>
              <strong>Config</strong>: {preview.cfg_file}
            </div>
            <div>
              <strong>Alignment</strong>: {preview.alignment ?? '—'}
            </div>
            <div>
              <strong>Data blocks</strong>: {preview.data_blocks.length}
            </div>
          </div>

          <div style={{ marginTop: 12 }}>
            <h4>Data block visualization</h4>
            {preview.data_blocks.length === 0 ? (
              <p>No [data_blocks] found in the config.</p>
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

            {preview.data_blocks.length > 0 && (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', textAlign: 'left' }}>
                  <thead>
                    <tr>
                      <th>Block</th>
                      <th>Range</th>
                      <th>Sites</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.data_blocks.map((b) => (
                      <tr key={b.name}>
                        <td>{b.name}</td>
                        <td style={{ fontFamily: 'monospace' }}>{b.range}</td>
                        <td>{b.length ?? '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      <label style={{ display: 'block', marginTop: 12 }}>
        Alignment file preview (optional)
        <input
          type="file"
          accept=".phy,.phylip,.nex,.nexus,.fasta,.fa,.fas,.txt"
          onChange={(e) => void onPickAlignment(e.target.files?.[0] ?? null)}
        />
      </label>

      {error && <p style={{ whiteSpace: 'pre-wrap' }}>{error}</p>}

      {props.state.alignmentPreview && (
        <div style={{ marginTop: 12 }}>
          <h3>Alignment preview</h3>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{props.state.alignmentPreview}</pre>
        </div>
      )}

      <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
        <button onClick={next}>Continue</button>
      </div>
    </div>
  )
}
