import { apiFetch, artifactUrl } from './client'
import type {
  ActionInfo,
  ArtifactResponse,
  AuthUser,
  CaseStudiesResponse,
  DefaultPlanInfo,
  JobResponse,
  JobStatusResponse,
  ModelsResponse,
  MuloDesignerStateResponse,
  MuloSimulateResponse,
  PlanInfo,
  ProjectDetail,
  ProjectSummary,
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
  register: (body: { email: string; password: string }) =>
    apiFetch<TokenResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  me: () => apiFetch<AuthUser>('/auth/me'),
  updateProfile: (body: {
    display_name?: string | null
    email?: string
    theme?: AuthUser['theme']
    current_password?: string
  }) =>
    apiFetch<AuthUser>('/auth/me', {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  changePassword: (body: { current_password: string; new_password: string }) =>
    apiFetch<void>('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  uploadAvatar: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return apiFetch<AuthUser>('/auth/me/avatar', { method: 'POST', body: form })
  },
  removeAvatar: () => apiFetch<AuthUser>('/auth/me/avatar', { method: 'DELETE' }),
}

export const adminApi = {
  listActions: () => apiFetch<ActionInfo[]>('/admin/actions'),
  listPlans: (params?: { active_only?: boolean }) => {
    const query = new URLSearchParams()
    if (params?.active_only) query.set('active_only', 'true')
    const suffix = query.toString() ? `?${query}` : ''
    return apiFetch<PlanInfo[]>(`/admin/plans${suffix}`)
  },
  createPlan: (body: {
    name: string
    description?: string
    price?: number
    actions?: string[]
    is_active?: boolean
  }) =>
    apiFetch<PlanInfo>('/admin/plans', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  updatePlan: (
    planId: number,
    body: {
      name?: string
      description?: string
      price?: number
      actions?: string[]
      is_active?: boolean
    },
  ) =>
    apiFetch<PlanInfo>(`/admin/plans/${planId}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  deletePlan: (planId: number) =>
    apiFetch<void>(`/admin/plans/${planId}`, { method: 'DELETE' }),
  getDefaultPlan: () => apiFetch<DefaultPlanInfo>('/admin/settings/default-plan'),
  setDefaultPlan: (planId: number) =>
    apiFetch<DefaultPlanInfo>('/admin/settings/default-plan', {
      method: 'PUT',
      body: JSON.stringify({ plan_id: planId }),
    }),
  listUsers: () => apiFetch<AuthUser[]>('/admin/users'),
  createUser: (body: {
    email: string
    password: string
    is_admin?: boolean
    plan_id?: number | null
  }) =>
    apiFetch<AuthUser>('/admin/users', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  updateUser: (
    userId: number,
    body: {
      is_active?: boolean
      is_admin?: boolean
      password?: string
      plan_id?: number | null
    },
  ) =>
    apiFetch<AuthUser>(`/admin/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  listProjects: (params?: { user_id?: number; pipeline_type?: string }) => {
    const query = new URLSearchParams()
    if (params?.user_id != null) query.set('user_id', String(params.user_id))
    if (params?.pipeline_type) query.set('pipeline_type', params.pipeline_type)
    const suffix = query.toString() ? `?${query}` : ''
    return apiFetch<ProjectSummary[]>(`/admin/projects${suffix}`)
  },
  getProject: (projectId: number) =>
    apiFetch<ProjectDetail>(`/admin/projects/${projectId}`),
  updateProject: (
    projectId: number,
    body: { title?: string; status?: string },
  ) =>
    apiFetch<ProjectDetail>(`/admin/projects/${projectId}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  deleteProject: (projectId: number) =>
    apiFetch<void>(`/admin/projects/${projectId}`, { method: 'DELETE' }),
}

export const projectsApi = {
  list: () => apiFetch<ProjectSummary[]>('/projects'),
  get: (projectId: number) => apiFetch<ProjectDetail>(`/projects/${projectId}`),
  create: (body: {
    title?: string
    pipeline_type: 'siloDesign' | 'muloDesign'
    file_name?: string
    file_type?: string
    file_content?: string
    control_objective?: string
  }) =>
    apiFetch<ProjectDetail>('/projects', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  update: (
    projectId: number,
    body: {
      title?: string
      status?: string
      control_objective?: string
      job_id?: string
      results?: Record<string, unknown>
    },
  ) =>
    apiFetch<ProjectDetail>(`/projects/${projectId}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  delete: (projectId: number) =>
    apiFetch<void>(`/projects/${projectId}`, { method: 'DELETE' }),
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
  start: (body: {
    config: Record<string, unknown>
    control_objective?: string
    project_id?: number | null
  }) =>
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
    project_id?: number | null
    file_name?: string
    file_type?: string
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
    project_id?: number | null
    file_name?: string
    file_type?: string
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
