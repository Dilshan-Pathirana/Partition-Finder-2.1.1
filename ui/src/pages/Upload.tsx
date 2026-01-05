import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

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
