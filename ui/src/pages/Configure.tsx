import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

export interface ConfigState {
  datatype: 'DNA' | 'protein' | 'morphology'
  modelsPreset: string
  criterion: 'aic' | 'aicc' | 'bic'
  search: string
  branchlengths: 'linked' | 'unlinked'
  cpus: number
}

export const defaultConfigState: ConfigState = {
  datatype: 'DNA',
  modelsPreset: 'all',
  criterion: 'aicc',
  search: 'greedy',
  branchlengths: 'linked',
  cpus: 1,
}

export default function ConfigurePage(props: {
  folder: string
  state: ConfigState
  onChange: (next: ConfigState) => void
}) {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  const overrides = useMemo(() => {
    return {
      models: props.state.modelsPreset,
      model_selection: props.state.criterion,
      search: props.state.search,
      branchlengths: props.state.branchlengths,
    }
  }, [props.state])

  function next() {
    setError(null)
    if (!props.folder.trim()) {
      setError('Missing folder path. Go back to Data Upload.')
      return
    }
    if (!props.state.search.trim()) {
      setError('Please choose a scheme search strategy.')
      return
    }
    if (!Number.isFinite(props.state.cpus) || props.state.cpus < 1) {
      setError('CPUs must be an integer ≥ 1.')
      return
    }
    // Persist overrides to sessionStorage for the Run step.
    sessionStorage.setItem('pf.new.folder', props.folder)
    sessionStorage.setItem('pf.new.overrides', JSON.stringify(overrides))
    sessionStorage.setItem('pf.new.datatype', props.state.datatype)
    sessionStorage.setItem('pf.new.cpus', String(Math.floor(props.state.cpus)))
    navigate('/new/run')
  }

  return (
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <h1>New analysis</h1>
        <Link to="/new/upload">Back</Link>
      </header>

      <h2>Configuration builder</h2>
      <p>Step 2 of 4 — Upload → Configure → Run → Interpret</p>

      <div style={{ display: 'grid', gap: 12, marginTop: 12 }}>
        <label>
          Datatype
          <select
            value={props.state.datatype}
            onChange={(e) => props.onChange({ ...props.state, datatype: e.target.value as any })}
          >
            <option value="DNA">DNA</option>
            <option value="protein">Protein</option>
            <option value="morphology">Morphology</option>
          </select>
        </label>

        <label>
          Models of evolution
          <select
            value={props.state.modelsPreset}
            onChange={(e) => props.onChange({ ...props.state, modelsPreset: e.target.value })}
          >
            <option value="all">all</option>
            <option value="allx">allx</option>
            <option value="mrbayes">mrbayes</option>
            <option value="beast">beast</option>
            <option value="gamma">gamma</option>
            <option value="gammai">gammai</option>
          </select>
        </label>

        <label>
          Criterion selection
          <select
            value={props.state.criterion}
            onChange={(e) => props.onChange({ ...props.state, criterion: e.target.value as any })}
          >
            <option value="aic">AIC</option>
            <option value="aicc">AICc</option>
            <option value="bic">BIC</option>
          </select>
        </label>

        <label>
          Scheme search strategy
          <select
            value={props.state.search}
            onChange={(e) => props.onChange({ ...props.state, search: e.target.value })}
          >
            <option value="greedy">greedy</option>
            <option value="all">all</option>
            <option value="user">user</option>
            <option value="rcluster">rcluster</option>
            <option value="rclusterf">rclusterf</option>
            <option value="kmeans">kmeans</option>
          </select>
        </label>

        <label>
          Branchlengths
          <select
            value={props.state.branchlengths}
            onChange={(e) =>
              props.onChange({ ...props.state, branchlengths: e.target.value as any })
            }
          >
            <option value="linked">linked</option>
            <option value="unlinked">unlinked</option>
          </select>
        </label>

        <label>
          CPUs (opt-in speedup)
          <input
            type="number"
            min={1}
            step={1}
            value={props.state.cpus}
            onChange={(e) => props.onChange({ ...props.state, cpus: Number(e.target.value) })}
          />
        </label>
      </div>

      {error && <p style={{ whiteSpace: 'pre-wrap' }}>{error}</p>}

      <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
        <button onClick={next}>Continue</button>
      </div>
    </div>
  )
}
