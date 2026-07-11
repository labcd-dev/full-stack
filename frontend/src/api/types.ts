export interface JobResponse {
  job_id: string
  module: string
  status: string
}

export interface JobStatusResponse {
  job_id: string
  module: string
  status: string
  metadata: Record<string, unknown>
  error?: string
}

export interface UploadResponse {
  file_name: string
  file_type: string
  file_content: string
}

export interface ModelsResponse {
  llm_models: string[]
  rag_models: string[]
}

export interface RegularizeResponse {
  file_content: string
  change_applied: boolean
  human_intervention: boolean
}

export interface StandardizeResponse {
  file_content: string
}

export interface RecommenderHandoffResponse {
  file_content: string
  chosen_controller: string
  trimming_params: Record<string, unknown>
  states_inputs: string[]
}

export interface TrimmerArtifactsResponse {
  result: Record<string, unknown>
  config: Record<string, unknown>
  pdf_file?: string
  safe_system_name: string
  output_dir: string
}

export interface CaseStudiesResponse {
  python: string[]
  matlab: string[]
  ga_json: string[]
}

export interface ArtifactResponse {
  job_id: string
  artifacts: Record<string, unknown>
}

export interface RagStatusResponse {
  next_step: 'comparison' | 'review'
  error_message: string
}

export type PipelineType = 'siloDesign' | 'muloDesign' | null

export interface StreamEvent {
  type: string
  mode?: string
  content?: unknown
  step?: string
  job_id?: string
  status?: string
  error?: string
  metadata?: Record<string, unknown>
}
