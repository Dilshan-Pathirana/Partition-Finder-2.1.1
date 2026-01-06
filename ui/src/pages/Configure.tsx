import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import WorkflowStepper from '../components/layout/WorkflowStepper'
import Button from '../components/ui/Button'
import { Card, CardBody, CardHeader } from '../components/ui/Card'
import { Input, Label, Select } from '../components/ui/Form'
import type { ConfigState } from '../state/newAnalysis'

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
    <div className="grid gap-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">New analysis</h1>
          <p className="mt-1 text-sm text-slate-600">Choose PartitionFinder options for this run.</p>
        </div>
        <Link to="/new/upload">
          <Button variant="ghost">Back</Button>
        </Link>
      </div>

      <WorkflowStepper active="configure" />

      <Card>
        <CardHeader title="Configuration" subtitle="These settings override the .cfg defaults" />
        <CardBody className="grid gap-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Label title="Datatype">
              <Select
                value={props.state.datatype}
                onChange={(e) =>
                  props.onChange({
                    ...props.state,
                    datatype: e.target.value as ConfigState['datatype'],
                  })
                }
              >
                <option value="DNA">DNA</option>
                <option value="protein">Protein</option>
                <option value="morphology">Morphology</option>
              </Select>
            </Label>

            <Label title="Models of evolution">
              <Select
                value={props.state.modelsPreset}
                onChange={(e) => props.onChange({ ...props.state, modelsPreset: e.target.value })}
              >
                <option value="all">all</option>
                <option value="allx">allx</option>
                <option value="mrbayes">mrbayes</option>
                <option value="beast">beast</option>
                <option value="gamma">gamma</option>
                <option value="gammai">gammai</option>
              </Select>
            </Label>

            <Label title="Criterion selection">
              <Select
                value={props.state.criterion}
                onChange={(e) =>
                  props.onChange({
                    ...props.state,
                    criterion: e.target.value as ConfigState['criterion'],
                  })
                }
              >
                <option value="aic">AIC</option>
                <option value="aicc">AICc</option>
                <option value="bic">BIC</option>
              </Select>
            </Label>

            <Label title="Scheme search strategy">
              <Select
                value={props.state.search}
                onChange={(e) => props.onChange({ ...props.state, search: e.target.value })}
              >
                <option value="greedy">greedy</option>
                <option value="all">all</option>
                <option value="user">user</option>
                <option value="rcluster">rcluster</option>
                <option value="rclusterf">rclusterf</option>
                <option value="kmeans">kmeans</option>
              </Select>
            </Label>

            <Label title="Branchlengths">
              <Select
                value={props.state.branchlengths}
                onChange={(e) =>
                  props.onChange({
                    ...props.state,
                    branchlengths: e.target.value as ConfigState['branchlengths'],
                  })
                }
              >
                <option value="linked">linked</option>
                <option value="unlinked">unlinked</option>
              </Select>
            </Label>

            <Label title="CPUs (opt-in speedup)" hint="Maps to legacy -p. Set 1 for deterministic single-process runs.">
              <Input
                type="number"
                min={1}
                step={1}
                value={props.state.cpus}
                onChange={(e) => props.onChange({ ...props.state, cpus: Number(e.target.value) })}
              />
            </Label>
          </div>

          {error && <pre className="whitespace-pre-wrap text-sm text-red-700">{error}</pre>}

          <div className="flex items-center justify-end gap-2">
            <Button onClick={next}>Continue</Button>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
