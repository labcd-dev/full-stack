import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { trimmerApi } from '../api/endpoints'
import { ActivityLog } from '../components/ActivityLog'
import { HumanInputForm } from '../components/HumanInputForm'
import { JsonViewer } from '../components/JsonViewer'
import { ProgressBar } from '../components/ProgressBar'
import { StatusMessage } from '../components/StatusMessage'
import { Tabs } from '../components/Tabs'
import { usePipeline } from '../context/PipelineContext'
import { useJobStream } from '../hooks/useJobStream'
import { btnPrimary, fieldInput, fieldLabel, pageIntro, pageSection } from '../lib/classes'

type Step = 'operating' | 'running' | 'results'

export function TrimmerPage() {
  const navigate = useNavigate()
  const pipeline = usePipeline()
  const [step, setStep] = useState<Step>('operating')
  const [activeTab, setActiveTab] = useState('process')
  const [selectedParams, setSelectedParams] = useState<string[]>([])
  const [paramValues, setParamValues] = useState<Record<string, string>>({})
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [artifacts, setArtifacts] = useState<Record<string, unknown> | null>(null)
  const [submittingInput, setSubmittingInput] = useState(false)

  const jobId = pipeline.trimmerJobId
  const stream = useJobStream({ module: 'trimmer', jobId, enabled: step === 'running' })

  useEffect(() => {
    const initial = Object.keys(pipeline.trimmingParams)
    if (initial.length > 0) {
      setSelectedParams(initial)
    } else if (pipeline.statesInputs.length > 0) {
      setSelectedParams([...pipeline.statesInputs])
    }
  }, [pipeline.trimmingParams, pipeline.statesInputs])

  const startTrimmer = async () => {
    const trimmingParams: Record<string, number> = {}
    for (const param of selectedParams) {
      const value = parseFloat(paramValues[param] ?? '0')
      trimmingParams[param] = Number.isNaN(value) ? 0 : value
    }

    setLoading(true)
    setError(null)
    try {
      const job = await trimmerApi.start({
        file_content: pipeline.fileContent,
        file_name: pipeline.fileName,
        model: pipeline.model,
        trimming_params: trimmingParams,
        states_inputs: pipeline.statesInputs,
      })
      pipeline.setTrimmerJobId(job.job_id)
      pipeline.setTrimmingParams(trimmingParams)
      setStep('running')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start trimmer')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (stream.isDone && step === 'running' && jobId) {
      void trimmerApi.artifacts(jobId).then((res) => {
        setArtifacts(res as unknown as Record<string, unknown>)
        setStep('results')
      })
    }
  }, [stream.isDone, step, jobId])

  const submitHumanInput = async (answer: string) => {
    if (!jobId || !stream.humanInput) return
    setSubmittingInput(true)
    try {
      await trimmerApi.input(jobId, {
        key: String(stream.humanInput.key ?? ''),
        prompt: String(stream.humanInput.prompt ?? ''),
        answer,
      })
      stream.clearHumanInput()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit input')
    } finally {
      setSubmittingInput(false)
    }
  }

  const goToMulo = () => navigate('/mulo')

  const tabs = [
    {
      id: 'process',
      label: step === 'results' ? 'Results' : 'Process',
      content: (
        <>
          {step === 'running' && (
            <>
              <ProgressBar value={stream.progress} label={stream.statusText || 'Running trimmer...'} />
              {stream.error && <StatusMessage type="error" message={stream.error} />}
              {stream.humanInput && (
                <HumanInputForm
                  request={stream.humanInput}
                  onSubmit={(answer) => void submitHumanInput(answer)}
                  disabled={submittingInput}
                />
              )}
            </>
          )}
          {step === 'results' && artifacts && (
            <>
              <StatusMessage type="success" message="Trimmer completed." />
              <JsonViewer data={artifacts.result ?? artifacts} title="Equilibrium Results" />
              <button type="button" className={btnPrimary} onClick={goToMulo}>
                Continue to Multi Loop Designer
              </button>
            </>
          )}
        </>
      ),
    },
    {
      id: 'logs',
      label: 'Activity Log',
      content: <ActivityLog logs={stream.logs} />,
    },
  ]

  return (
    <section className={pageSection}>
      <h2 className="mt-0 text-foreground">Trimmer Workspace</h2>
      {error && <StatusMessage type="error" message={error} />}

      {step === 'operating' && (
        <>
          <h3 className="text-foreground">Specify Operating Point</h3>
          <p className={pageIntro}>
            Select parameters and assign floating-point values for trimming.
          </p>

          {pipeline.statesInputs.length === 0 ? (
            <StatusMessage type="warning" message="No parameters available. Complete Recommender handoff first." />
          ) : (
            <>
              <div className="flex flex-col gap-2">
                {pipeline.statesInputs.map((param) => (
                  <label key={param} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={selectedParams.includes(param)}
                      onChange={(e) =>
                        setSelectedParams((prev) =>
                          e.target.checked
                            ? [...prev, param]
                            : prev.filter((p) => p !== param),
                        )
                      }
                    />
                    {param}
                  </label>
                ))}
              </div>

              {selectedParams.map((param) => (
                <label key={param} className={fieldLabel}>
                  <span>{param}</span>
                  <input
                    type="number"
                    step="any"
                    className={fieldInput}
                    value={paramValues[param] ?? ''}
                    onChange={(e) =>
                      setParamValues((prev) => ({ ...prev, [param]: e.target.value }))
                    }
                  />
                </label>
              ))}

              <button
                type="button"
                className={btnPrimary}
                disabled={loading || selectedParams.length === 0 || !pipeline.fileContent}
                onClick={() => void startTrimmer()}
              >
                Start Trimmer
              </button>
            </>
          )}
        </>
      )}

      {(step === 'running' || step === 'results') && (
        <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
      )}
    </section>
  )
}
