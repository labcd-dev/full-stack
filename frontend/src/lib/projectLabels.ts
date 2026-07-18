import type { ProjectPipelineType, ProjectStatus } from '../api/types'

export function pipelineLabel(pipeline: ProjectPipelineType | string): string {
  if (pipeline === 'siloDesign') return 'Single Loop'
  if (pipeline === 'muloDesign') return 'Multi Loop'
  return pipeline
}

export function statusBadgeClass(status: ProjectStatus | string): string {
  const base = 'rounded-md px-2 py-0.5 text-xs font-medium capitalize'
  switch (status) {
    case 'completed':
      return `${base} bg-[var(--app-status-success-bg)] text-[var(--app-status-success-text)]`
    case 'running':
      return `${base} bg-[var(--app-status-info-bg)] text-[var(--app-status-info-text)]`
    case 'failed':
      return `${base} bg-[var(--app-status-error-bg)] text-[var(--app-status-error-text)]`
    case 'cancelled':
      return `${base} bg-[var(--app-status-warning-bg)] text-[var(--app-status-warning-text)]`
    default:
      return `${base} bg-surface-muted text-muted-text`
  }
}
