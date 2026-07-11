import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { healthApi, regularizerApi, uploadApi } from '../api/endpoints'
import { CodePreview } from '../components/CodePreview'
import { FileUpload } from '../components/FileUpload'
import { ModelSelect } from '../components/ModelSelect'
import { StatusMessage } from '../components/StatusMessage'
import { usePipeline } from '../context/PipelineContext'
import {
  btnBase,
  btnPrimary,
  btnWide,
  cardProcessing,
  pageIntro,
  pageSection,
  pageTitle,
} from '../lib/classes'

type Stage = 'upload' | 'processing' | 'result' | 'standardizing' | 'ready'

export function HomePage() {
  const navigate = useNavigate()
  const pipeline = usePipeline()
  const [stage, setStage] = useState<Stage>('upload')
  const [models, setModels] = useState<string[]>(['gpt-4o'])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [editMode, setEditMode] = useState(false)

  useEffect(() => {
    healthApi.models().then((res) => setModels(res.llm_models)).catch(() => {})
  }, [])

  const handleFileSelect = async (file: File) => {
    setError(null)
    setLoading(true)
    try {
      const uploaded = await uploadApi.upload(file)
      pipeline.setFile(uploaded.file_name, uploaded.file_type, uploaded.file_content)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const runRegularizer = async () => {
    if (!pipeline.fileContent) return
    setLoading(true)
    setError(null)
    setStage('processing')
    try {
      const result = await regularizerApi.regularize({
        file_content: pipeline.fileContent,
        file_name: pipeline.fileName,
        file_type: pipeline.fileType,
        model: pipeline.model,
      })
      pipeline.setRegularizeResult(
        result.file_content,
        result.change_applied,
        result.human_intervention,
      )
      if (!result.change_applied) {
        setStage('standardizing')
        const standardized = await regularizerApi.standardize({
          file_content: result.file_content,
          model: pipeline.model,
          silo_pipeline: pipeline.pipeline === 'siloDesign',
        })
        pipeline.updateFileContent(standardized.file_content)
        setStage('ready')
      } else {
        setStage('result')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Regularization failed')
      setStage('upload')
    } finally {
      setLoading(false)
    }
  }

  const runStandardize = async () => {
    setLoading(true)
    setError(null)
    setStage('standardizing')
    try {
      const result = await regularizerApi.standardize({
        file_content: pipeline.fileContent,
        model: pipeline.model,
        silo_pipeline: pipeline.pipeline === 'siloDesign',
      })
      pipeline.updateFileContent(result.file_content)
      setStage('ready')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Standardization failed')
      setStage('result')
    } finally {
      setLoading(false)
    }
  }

  const proceedToPipeline = () => {
    if (pipeline.pipeline === 'muloDesign') {
      navigate('/recommender')
    } else if (pipeline.pipeline === 'siloDesign') {
      navigate('/silo')
    }
  }

  return (
    <section className={pageSection}>
      <h2 className={pageTitle}>Control Design Setup</h2>
      <p className={pageIntro}>
        Upload a system definition file, choose a pipeline, and start the design process.
      </p>

      {error && <StatusMessage type="error" message={error} />}

      {stage === 'upload' && (
        <>
          <div className="grid grid-cols-[2fr_1fr] gap-4 mb-4 max-md:grid-cols-1">
            <FileUpload onFileSelect={handleFileSelect} disabled={loading} />
            <ModelSelect
              models={models}
              value={pipeline.model}
              onChange={pipeline.setModel}
            />
          </div>

          {pipeline.fileContent && (
            <StatusMessage
              type="success"
              message={`File loaded: ${pipeline.fileName} (${pipeline.fileType})`}
            />
          )}

          <div className="flex gap-3 flex-wrap mt-4">
            <button
              type="button"
              className={pipeline.pipeline === 'siloDesign' ? btnPrimary : btnBase}
              onClick={() => pipeline.setPipeline('siloDesign')}
            >
              Single Loop Control Design
            </button>
            <button
              type="button"
              className={pipeline.pipeline === 'muloDesign' ? btnPrimary : btnBase}
              onClick={() => pipeline.setPipeline('muloDesign')}
            >
              Multi Loop Control Design
            </button>
          </div>

          {pipeline.pipeline && pipeline.fileContent && (
            <button
              type="button"
              className={`${btnPrimary} ${btnWide}`}
              disabled={loading}
              onClick={() => void runRegularizer()}
            >
              Start Process
            </button>
          )}
        </>
      )}

      {stage === 'processing' && (
        <div className={cardProcessing}>
          <Loader2 className="size-8 text-primary animate-spin mx-auto mb-3" aria-hidden />
          <h3 className="text-foreground mt-0">Processing file...</h3>
          <p className="text-muted-text mb-0">Evaluating syntax and fixing errors via API.</p>
        </div>
      )}

      {stage === 'standardizing' && (
        <div className={cardProcessing}>
          <Loader2 className="size-8 text-primary animate-spin mx-auto mb-3" aria-hidden />
          <h3 className="text-foreground mt-0">Standardizing code...</h3>
          <p className="text-muted-text mb-0">Generating standard format Python file via API.</p>
        </div>
      )}

      {stage === 'result' && pipeline.changeApplied && (
        <>
          <h3 className="text-foreground">Code Pre-Processing Result</h3>
          {pipeline.fileType === 'matlab' && (
            <StatusMessage type="success" message="MATLAB file converted to Python." />
          )}
          {pipeline.changeApplied && !pipeline.humanIntervention && (
            <StatusMessage type="success" message="Syntax errors auto-repaired." />
          )}
          {pipeline.humanIntervention && (
            <StatusMessage
              type="warning"
              message="Automated fixer could not resolve all syntax issues. Review and edit the code."
            />
          )}

          {!editMode ? (
            <>
              <CodePreview value={pipeline.fileContent} readOnly />
              <div className="flex gap-3 flex-wrap mt-4">
                <button type="button" className={btnBase} onClick={() => setEditMode(true)}>
                  Edit Code
                </button>
                <button type="button" className={btnPrimary} onClick={() => void runStandardize()}>
                  Continue
                </button>
              </div>
            </>
          ) : (
            <>
              <CodePreview
                value={pipeline.fileContent}
                onChange={pipeline.updateFileContent}
              />
              <div className="flex gap-3 flex-wrap mt-4">
                <button
                  type="button"
                  className={btnPrimary}
                  onClick={() => setEditMode(false)}
                >
                  Save Changes
                </button>
                <button type="button" className={btnBase} onClick={() => setEditMode(false)}>
                  Cancel
                </button>
              </div>
            </>
          )}
        </>
      )}

      {stage === 'ready' && (
        <>
          <StatusMessage type="success" message="File is ready for the selected pipeline." />
          <CodePreview value={pipeline.fileContent} readOnly height={300} />
          <button type="button" className={`${btnPrimary} ${btnWide}`} onClick={proceedToPipeline}>
            Continue to {pipeline.pipeline === 'muloDesign' ? 'Recommender' : 'Silo Designer'}
          </button>
        </>
      )}
    </section>
  )
}
