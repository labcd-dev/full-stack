import { useCallback, useEffect, useState } from 'react'
import { healthApi, siloApi } from '../api/endpoints'
import { ActivityLog } from '../components/ActivityLog'
import { DesignIterationReport } from '../components/DesignIterationReport'
import { DesignMonitorDashboard } from '../components/DesignMonitorDashboard'
import { CodePreview } from '../components/CodePreview'
import { JsonViewer } from '../components/JsonViewer'
import { ModelSelect } from '../components/ModelSelect'
import { ProgressBar } from '../components/ProgressBar'
import { StatusMessage } from '../components/StatusMessage'
import { Tabs } from '../components/Tabs'
import { usePipeline } from '../context/PipelineContext'
import { useJobStream } from '../hooks/useJobStream'
import { usePoll } from '../hooks/usePoll'
import {
  btnLink,
  btnPrimary,
  btnWide,
  cardPanel,
  fieldCheckbox,
  fieldInput,
  fieldLabel,
  mutedText,
  pageIntro,
  pageSection,
} from '../lib/classes'

export function SiloPage() {
  const pipeline = usePipeline()
  const [models, setModels] = useState<string[]>(['gpt-4o'])
  const [objective, setObjective] = useState('')
  const [activeTab, setActiveTab] = useState('monitor')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [started, setStarted] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [gaEnabled, setGaEnabled] = useState(true)

  const jobId = pipeline.siloJobId
  const stream = useJobStream({ module: 'silo', jobId, enabled: started })

  const fetchMonitor = useCallback(async () => {
    if (!jobId) return null
    return siloApi.monitor(jobId)
  }, [jobId])

  const poll = usePoll(fetchMonitor, 2000, started && !stream.isDone)

  useEffect(() => {
    healthApi.models().then((res) => setModels(res.llm_models)).catch(() => {})
  }, [])

  const startDesign = async () => {
    if (!pipeline.fileContent) {
      setError('Upload and process a file on the Home page first.')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const config: Record<string, unknown> = {
        llm_model: pipeline.model,
        file_content: pipeline.fileContent,
        file_type: pipeline.fileType === 'matlab' ? 'MATLAB/Octave (.m)' : 'Python (.py)',
        enable_ga: gaEnabled,
        dt: 0.01,
        max_time: 5.0,
        target: 0.0,
      }

      const job = await siloApi.start({
        config,
        control_objective: objective,
      })
      pipeline.setSiloJobId(job.job_id)
      setStarted(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start silo design')
    } finally {
      setLoading(false)
    }
  }

  const monitorState = poll.data as Record<string, unknown> | null
  const llmResponses = (monitorState?.llm_responses ?? []) as Array<Record<string, unknown>>
  const progressHistory = (monitorState?.progress_history ?? []) as Array<Record<string, unknown>>
  const stateHistory = (monitorState?.state_history ?? []) as Array<Record<string, unknown>>
  const currentState = (monitorState?.current_state ?? null) as Record<string, unknown> | null
  const pollProgress =
    progressHistory.length > 0 ? Math.min(progressHistory.length * 5, 95) / 100 : 0
  const latestProgress = stream.isDone ? 1 : Math.max(pollProgress, stream.progress)
  const latestMessage =
    progressHistory.length > 0
      ? String(progressHistory[progressHistory.length - 1]?.message ?? '')
      : ''

  const tabs = [
    {
      id: 'monitor',
      label: 'Design Monitor',
      content: (
        <>
          {started && (
            <ProgressBar
              value={latestProgress}
              label={
                stream.isDone
                  ? 'Design complete'
                  : latestMessage || stream.statusText || 'Running single-loop design...'
              }
            />
          )}
          {stream.error && <StatusMessage type="error" message={stream.error} />}
          {stateHistory.length > 0 && (
            <DesignMonitorDashboard
              stateHistory={stateHistory}
              currentState={currentState}
            />
          )}
          {llmResponses.length > 0 && (
            <DesignIterationReport responses={llmResponses} />
          )}
          {!started && (
            <p className={mutedText}>Start a design to see live monitor data from the API.</p>
          )}
        </>
      ),
    },
    {
      id: 'logs',
      label: 'Activity Log',
      content: <ActivityLog logs={stream.logs} />,
    },
    {
      id: 'state',
      label: 'Monitor State',
      content: monitorState ? (
        <JsonViewer data={monitorState} />
      ) : (
        <p className={mutedText}>No monitor state yet.</p>
      ),
    },
  ]

  return (
    <section className={pageSection}>
      <h2 className="mt-0 text-foreground">Single Loop Control Designer</h2>
      <p className={pageIntro}>
        Describe your control objective and run the SiloDesigner pipeline via API.
      </p>

      {error && <StatusMessage type="error" message={error} />}

      {!started && (
        <>
          <label className={fieldLabel}>
            <span>Control Objective</span>
            <textarea
              className={fieldInput}
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              rows={4}
              placeholder="Describe what you want the controller to achieve..."
            />
          </label>

          <ModelSelect models={models} value={pipeline.model} onChange={pipeline.setModel} />

          <button type="button" className={btnLink} onClick={() => setShowAdvanced((v) => !v)}>
            {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
          </button>

          {showAdvanced && (
            <div className={`${cardPanel} mt-4`}>
              <label className={fieldCheckbox}>
                <input
                  type="checkbox"
                  checked={gaEnabled}
                  onChange={(e) => setGaEnabled(e.target.checked)}
                />
                Enable GA Optimization
              </label>
            </div>
          )}

          {pipeline.fileContent && (
            <details>
              <summary>Uploaded Dynamics Preview</summary>
              <CodePreview value={pipeline.fileContent} readOnly height={200} />
            </details>
          )}

          <button
            type="button"
            className={`${btnPrimary} ${btnWide}`}
            disabled={loading || !pipeline.fileContent}
            onClick={() => void startDesign()}
          >
            Start Design
          </button>
        </>
      )}

      {started && <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />}
    </section>
  )
}
