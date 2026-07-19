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
  trimming_params: string[]
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
  mulo: string[]
  mulo_objectives: Record<string, string>
}

export interface ArtifactResponse {
  job_id: string
  artifacts: Record<string, unknown>
}

export interface RagStatusResponse {
  next_step: 'comparison' | 'review'
  error_message: string
}

export interface MuloDesignerStateResponse {
  job_id: string
  controller_index: number
  controller_designed: boolean
  total_loops: number
  loop_name: string
  is_complete: boolean
  equation: string
  controller_structure: Record<string, unknown>[]
  case_study: Record<string, unknown>
  run_config: Record<string, unknown>
  final_state: Record<string, unknown>
  modified_code: string
  modified_controller_structure: Record<string, unknown>[]
  pid_gains: { Kp: number; Ki: number; Kd: number }
  pid_gain_bounds: { Kp: number; Ki: number; Kd: number }
}

export interface MuloSimulateResponse {
  signal_type: string
  time: number[]
  actual: number[]
  reference: number[]
  y_label: string
  unit: string
  code: string
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

export type ThemeMode = 'light' | 'dark' | 'system'

export interface AuthUser {
  id: number
  email: string
  display_name: string | null
  avatar_url: string | null
  theme: ThemeMode
  is_admin: boolean
  is_active: boolean
  plan_id: number | null
  plan_name: string | null
  actions: string[]
  created_at: string
}

export interface ActionInfo {
  code: string
  description: string
}

export interface PlanInfo {
  id: number
  name: string
  description: string
  price: number
  is_active: boolean
  actions: string[]
  created_at: string
}

export interface DefaultPlanInfo {
  plan_id: number | null
  plan: PlanInfo | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export type ProjectPipelineType = 'siloDesign' | 'muloDesign'
export type ProjectStatus = 'draft' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface ProjectSummary {
  id: number
  user_id: number
  owner_email?: string | null
  title: string
  pipeline_type: ProjectPipelineType
  status: ProjectStatus
  file_name: string
  file_type: string
  has_results: boolean
  job_id?: string | null
  created_at: string
  updated_at: string
}

export interface ProjectDetail extends ProjectSummary {
  file_content: string
  control_objective?: string | null
  results?: Record<string, unknown> | null
}

