import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { FolderOpen, Search, Trash2 } from 'lucide-react'
import { projectsApi } from '../api/endpoints'
import type { ProjectSummary } from '../api/types'
import { StatusMessage } from '../components/StatusMessage'
import {
  btnBase,
  btnCompact,
  btnPrimary,
  cardPanel,
  fieldInput,
  pageIntro,
  pageSection,
} from '../lib/classes'
import { pipelineLabel, statusBadgeClass } from '../lib/projectLabels'

export function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState<'all' | 'siloDesign' | 'muloDesign'>('all')

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      setProjects(await projectsApi.list())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return projects.filter((project) => {
      if (filter !== 'all' && project.pipeline_type !== filter) return false
      if (!q) return true
      return (
        project.title.toLowerCase().includes(q) ||
        project.file_name.toLowerCase().includes(q) ||
        project.status.toLowerCase().includes(q)
      )
    })
  }, [projects, query, filter])

  const handleDelete = async (projectId: number) => {
    if (!window.confirm('Delete this project? This cannot be undone.')) return
    try {
      await projectsApi.delete(projectId)
      setProjects((prev) => prev.filter((p) => p.id !== projectId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete project')
    }
  }

  return (
    <section className={pageSection}>
      <header className="space-y-2">
        <h2 className="m-0 text-2xl font-semibold tracking-tight text-foreground">
          Project history
        </h2>
        <p className={`${pageIntro} m-0 max-w-2xl`}>
          Browse Single Loop and Multi Loop projects you created, including uploaded files and
          saved design results.
        </p>
      </header>

      {error && <StatusMessage type="error" message={error} />}

      <div className={`${cardPanel} flex flex-col gap-3 sm:flex-row sm:items-center`}>
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" />
          <input
            className={`${fieldInput} w-full pl-9`}
            placeholder="Search by title, file, or status"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="flex gap-1">
          {(
            [
              ['all', 'All'],
              ['siloDesign', 'Single Loop'],
              ['muloDesign', 'Multi Loop'],
            ] as const
          ).map(([value, label]) => (
            <button
              key={value}
              type="button"
              className={`${btnBase} ${btnCompact} ${
                filter === value
                  ? 'border-primary bg-[color-mix(in_srgb,var(--app-primary)_12%,transparent)] text-primary'
                  : ''
              }`}
              onClick={() => setFilter(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <p className="text-muted-text">Loading projects…</p>
      ) : filtered.length === 0 ? (
        <div className={`${cardPanel} text-center`}>
          <FolderOpen className="mx-auto mb-3 size-10 text-muted" />
          <p className="m-0 text-foreground font-medium">No projects yet</p>
          <p className="mt-1 mb-4 text-sm text-muted-text">
            Upload a dynamics file on Home and start a Single or Multi Loop design.
          </p>
          <Link to="/" className={btnPrimary}>
            Go to Home
          </Link>
        </div>
      ) : (
        <ul className="m-0 grid list-none gap-3 p-0">
          {filtered.map((project) => (
            <li key={project.id} className={`${cardPanel} flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between`}>
              <div className="min-w-0 space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <Link
                    to={`/projects/${project.id}`}
                    className="truncate text-base font-semibold text-foreground hover:text-primary"
                  >
                    {project.title}
                  </Link>
                  <span className={statusBadgeClass(project.status)}>{project.status}</span>
                  <span className="rounded-md bg-surface-muted px-2 py-0.5 text-xs text-muted-text">
                    {pipelineLabel(project.pipeline_type)}
                  </span>
                </div>
                <p className="m-0 text-sm text-muted-text">
                  File: {project.file_name || '—'} · Updated{' '}
                  {new Date(project.updated_at).toLocaleString()}
                  {project.has_results ? ' · Has results' : ''}
                </p>
              </div>
              <div className="flex shrink-0 gap-2">
                <Link to={`/projects/${project.id}`} className={`${btnBase} ${btnCompact}`}>
                  View
                </Link>
                <button
                  type="button"
                  className={`${btnBase} ${btnCompact}`}
                  onClick={() => void handleDelete(project.id)}
                  title="Delete project"
                >
                  <Trash2 className="size-3.5" />
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
