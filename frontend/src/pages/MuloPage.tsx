import { useEffect, useState } from 'react'
import { caseStudiesApi, muloApi } from '../api/endpoints'
import { JsonViewer } from '../components/JsonViewer'
import { ProgressBar } from '../components/ProgressBar'
import { StatusMessage } from '../components/StatusMessage'
import { Tabs } from '../components/Tabs'
import { usePipeline } from '../context/PipelineContext'
import { useJobStream } from '../hooks/useJobStream'
import { usePoll } from '../hooks/usePoll'
import {
  btnBase,
  btnPrimary,
  btnWide,
  codePreview,
  fieldInput,
  fieldLabel,
  pageIntro,
  pageSection,
} from '../lib/classes'

const DEFAULT_MULO_RUN_CONFIG = {
  case_study_file: '',
  seed: 42,
  llm_model: 'gpt-4o-mini',
  web_search_model: null,
  max_attempts: 5,
  buffer_size: 3,
  max_wall_clock: 120,
  max_cost_budget: 1,
  prompt_variant: 'elaborate',
}

export function MuloPage() {
  const pipeline = usePipeline()
  const [caseStudies, setCaseStudies] = useState<string[]>([])
  const [selectedCase, setSelectedCase] = useState('')
  const [equation, setEquation] = useState(pipeline.fileContent)
  const [runConfigJson, setRunConfigJson] = useState(
    () => JSON.stringify(DEFAULT_MULO_RUN_CONFIG, null, 2),
  )
  const [controllerStructureJson, setControllerStructureJson] = useState('[]')
  const [systemIdJson, setSystemIdJson] = useState('{}')
  const [trimmingResultJson, setTrimmingResultJson] = useState('{}')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [started, setStarted] = useState(false)
  const [activeTab, setActiveTab] = useState('process')
  const [plotData, setPlotData] = useState<Record<string, unknown> | null>(null)

  const jobId = pipeline.muloJobId
  const stream = useJobStream({ module: 'mulo', jobId, enabled: started })

  useEffect(() => {
    caseStudiesApi.list().then((res) => {
      setCaseStudies(res.ga_json)
      if (res.ga_json.length > 0) setSelectedCase(res.ga_json[0])
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (pipeline.fileContent) setEquation(pipeline.fileContent)
  }, [pipeline.fileContent])

  const fetchPlotData = async () => {
    if (!jobId) return null
    return muloApi.plotData(jobId)
  }

  const poll = usePoll(fetchPlotData, 2000, started && !stream.isDone)

  useEffect(() => {
    if (poll.data) setPlotData(poll.data as Record<string, unknown>)
  }, [poll.data])

  useEffect(() => {
    if (stream.isDone && jobId) {
      void muloApi.plotData(jobId).then(setPlotData).catch(() => {})
    }
  }, [stream.isDone, jobId])

  const startMulo = async () => {
    setLoading(true)
    setError(null)
    try {
      const job = await muloApi.start({
        run_config: JSON.parse(runConfigJson),
        controller_structure: JSON.parse(controllerStructureJson),
        system_identification: JSON.parse(systemIdJson),
        trimming_result: JSON.parse(trimmingResultJson),
        equation,
      })
      pipeline.setMuloJobId(job.job_id)
      setStarted(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start MuloDesigner')
    } finally {
      setLoading(false)
    }
  }

  const loadFromTrimmer = () => {
    if (pipeline.handoff) {
      setEquation(pipeline.handoff.file_content)
    }
    setTrimmingResultJson(JSON.stringify(pipeline.trimmingParams, null, 2))
  }

  const tabs = [
    {
      id: 'process',
      label: 'GA Optimization',
      content: (
        <>
          {started && (
            <ProgressBar
              value={stream.progress}
              label={stream.isDone ? 'Optimization complete' : 'Running GA optimization...'}
            />
          )}
          {stream.error && <StatusMessage type="error" message={stream.error} />}
          {plotData && Object.keys(plotData).length > 0 && (
            <JsonViewer data={plotData} title="Plot Data (from API)" />
          )}
        </>
      ),
    },
    {
      id: 'events',
      label: 'Stream Events',
      content: (
        <div className="flex flex-col gap-3">
          {stream.events.map((event, index) => (
            <pre
              key={index}
              className="m-0 whitespace-pre-wrap break-words font-mono text-[0.82rem] text-foreground-secondary"
            >
              {JSON.stringify(event, null, 2)}
            </pre>
          ))}
        </div>
      ),
    },
  ]

  return (
    <section className={pageSection}>
      <h2 className="mt-0 text-foreground">Multi Loop Control Designer</h2>
      <p className={pageIntro}>
        LLM-enhanced genetic algorithm for multi-loop PID controller design.
      </p>

      {error && <StatusMessage type="error" message={error} />}

      {!started && (
        <>
          <div className="grid grid-cols-[2fr_1fr] gap-4 mb-4 max-md:grid-cols-1">
            <label className={fieldLabel}>
              <span>Case Study (JSON)</span>
              <select
                className={fieldInput}
                value={selectedCase}
                onChange={(e) => setSelectedCase(e.target.value)}
              >
                {caseStudies.map((name) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ))}
              </select>
            </label>
            <button type="button" className={`${btnBase} self-end`} onClick={loadFromTrimmer}>
              Load from Trimmer Handoff
            </button>
          </div>

          <label className={fieldLabel}>
            <span>Equation</span>
            <textarea
              className={codePreview}
              value={equation}
              onChange={(e) => setEquation(e.target.value)}
              rows={6}
            />
          </label>

          <label className={fieldLabel}>
            <span>Run Config (JSON)</span>
            <textarea
              className={codePreview}
              value={runConfigJson}
              onChange={(e) => setRunConfigJson(e.target.value)}
              rows={4}
            />
          </label>

          <label className={fieldLabel}>
            <span>Controller Structure (JSON array)</span>
            <textarea
              className={codePreview}
              value={controllerStructureJson}
              onChange={(e) => setControllerStructureJson(e.target.value)}
              rows={4}
            />
          </label>

          <label className={fieldLabel}>
            <span>System Identification (JSON)</span>
            <textarea
              className={codePreview}
              value={systemIdJson}
              onChange={(e) => setSystemIdJson(e.target.value)}
              rows={4}
            />
          </label>

          <label className={fieldLabel}>
            <span>Trimming Result (JSON)</span>
            <textarea
              className={codePreview}
              value={trimmingResultJson}
              onChange={(e) => setTrimmingResultJson(e.target.value)}
              rows={4}
            />
          </label>

          <button
            type="button"
            className={`${btnPrimary} ${btnWide}`}
            disabled={loading || !equation.trim()}
            onClick={() => void startMulo()}
          >
            Start Multi Loop Design
          </button>
        </>
      )}

      {started && <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />}
    </section>
  )
}
