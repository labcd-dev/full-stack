import { apiFetch, artifactUrl } from './client'
import type {
  ActionInfo,
  ArtifactResponse,
  AuthUser,
  CaseStudiesResponse,
  JobResponse,
  JobStatusResponse,
  ModelsResponse,
  MuloDesignerStateResponse,
  MuloSimulateResponse,
  RagStatusResponse,
  RecommenderHandoffResponse,
  RegularizeResponse,
  StandardizeResponse,
  TokenResponse,
  TrimmerArtifactsResponse,
  UploadResponse,
} from './types'

export const authApi = {
  login: (body: { email: string; password: string }) =>
    apiFetch<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  me: () => apiFetch<AuthUser>('/auth/me'),
}

export const adminApi = {
  listActions: () => apiFetch<ActionInfo[]>('/admin/actions'),
  listUsers: () => apiFetch<AuthUser[]>('/admin/users'),
  createUser: (body: {
    email: string
    password: string
    is_admin?: boolean
    actions?: string[]
  }) =>
    apiFetch<AuthUser>('/admin/users', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  setUserActions: (userId: number, actions: string[]) =>
    apiFetch<AuthUser>(`/admin/users/${userId}/actions`, {
      method: 'PUT',
      body: JSON.stringify({ actions }),
    }),
  updateUser: (
    userId: number,
    body: { is_active?: boolean; is_admin?: boolean; password?: string },
  ) =>
    apiFetch<AuthUser>(`/admin/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
}

export const healthApi = {
  check: () => apiFetch<{ status: string }>('/health'),
  models: () => apiFetch<ModelsResponse>('/models'),
}

export const uploadApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return apiFetch<UploadResponse>('/upload', { method: 'POST', body: form })
  },
}

export const regularizerApi = {
  regularize: (body: {
    file_content: string
    file_name?: string
    file_type?: string
    model?: string
  }) =>
    apiFetch<RegularizeResponse>('/regularize', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  standardize: (body: {
    file_content: string
    model?: string
    silo_pipeline?: boolean
  }) =>
    apiFetch<StandardizeResponse>('/regularize/standardize', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
}

export const recommenderApi = {
  start: (body: {
    file_content: string
    file_name: string
    model?: string
    step?: string
  }) =>
    apiFetch<JobResponse>('/recommender/start', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  state: (jobId: string) =>
    apiFetch<Record<string, unknown>>(`/recommender/${jobId}/state`),

  ragDecision: (jobId: string, body: { flags: string[]; model?: string }) =>
    apiFetch<JobResponse>(`/recommender/${jobId}/rag-decision`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  ragStatus: (jobId: string) =>
    apiFetch<RagStatusResponse>(`/recommender/${jobId}/rag-status`),

  handoff: (jobId: string, body: { chosen_controller?: string | null }) =>
    apiFetch<RecommenderHandoffResponse>(`/recommender/${jobId}/handoff`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
}

export const trimmerApi = {
  start: (body: {
    file_content: string
    file_name: string
    model?: string
    trimming_params?: Record<string, unknown>
    states_inputs?: string[]
  }) =>
    apiFetch<JobResponse>('/trimmer/start', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  input: (jobId: string, body: { key: string; prompt: string; answer: string }) =>
    apiFetch<JobResponse>(`/trimmer/${jobId}/input`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  artifacts: (jobId: string) =>
    apiFetch<TrimmerArtifactsResponse>(`/trimmer/${jobId}/artifacts`),
}

export const siloApi = {
  start: (body: { config: Record<string, unknown>; control_objective?: string }) =>
    apiFetch<JobResponse>('/silo/start', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  monitor: (jobId: string) =>
    apiFetch<Record<string, unknown>>(`/silo/${jobId}/monitor`),
}

export const muloApi = {
  init: (body: {
    run_config: Record<string, unknown>
    controller_structure: Record<string, unknown>[]
    system_identification: Record<string, unknown>
    trimming_result: Record<string, unknown>
    equation: string
  }) =>
    apiFetch<JobResponse>('/mulo/init', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  start: (body: {
    run_config: Record<string, unknown>
    controller_structure: Record<string, unknown>[]
    system_identification: Record<string, unknown>
    trimming_result: Record<string, unknown>
    equation: string
  }) =>
    apiFetch<JobResponse>('/mulo/start', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  configure: (
    jobId: string,
    body: { case_study: Record<string, unknown>; controller_structure: Record<string, unknown>[] },
  ) =>
    apiFetch<JobResponse>(`/mulo/${jobId}/configure`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  run: (jobId: string) =>
    apiFetch<JobResponse>(`/mulo/${jobId}/run`, {
      method: 'POST',
    }),

  continue: (
    jobId: string,
    body: { equation: string; controller_structure: Record<string, unknown>[] },
  ) =>
    apiFetch<JobResponse>(`/mulo/${jobId}/continue`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  state: (jobId: string) => apiFetch<MuloDesignerStateResponse>(`/mulo/${jobId}/state`),

  simulate: (
    jobId: string,
    body: { kp: number; ki: number; kd: number; signal_type: string },
  ) =>
    apiFetch<MuloSimulateResponse>(`/mulo/${jobId}/simulate`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  scratchpad: (
    jobId: string,
    body: { modified_code: string; modified_controller_structure: Record<string, unknown>[] },
  ) =>
    apiFetch<JobResponse>(`/mulo/${jobId}/scratchpad`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  plotData: (jobId: string) =>
    apiFetch<Record<string, unknown>>(`/mulo/${jobId}/plot-data`),
}

export const jobsApi = {
  status: (jobId: string) => apiFetch<JobStatusResponse>(`/jobs/${jobId}`),
  cancel: (jobId: string) =>
    apiFetch<JobStatusResponse>(`/jobs/${jobId}/cancel`, { method: 'POST' }),
  results: (jobId: string) => apiFetch<ArtifactResponse>(`/jobs/${jobId}/results`),
  downloadArtifact: artifactUrl,
}

export const caseStudiesApi = {
  list: () => apiFetch<CaseStudiesResponse>('/case-studies'),
  mulo: (name: string) =>
    apiFetch<Record<string, unknown>>(`/case-studies/mulo/${encodeURIComponent(name)}`),
}
