import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FolderKanban, Shield, UserCheck, Users, Zap } from 'lucide-react'
import { adminApi } from '../api/endpoints'
import type { ActionInfo, AuthUser, ProjectSummary } from '../api/types'
import { StatusMessage } from '../components/StatusMessage'
import { btnPrimary, cardPanel } from '../lib/classes'

export function AdminOverviewPage() {
  const [users, setUsers] = useState<AuthUser[]>([])
  const [actions, setActions] = useState<ActionInfo[]>([])
  const [projects, setProjects] = useState<ProjectSummary[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const [userList, actionList, projectList] = await Promise.all([
          adminApi.listUsers(),
          adminApi.listActions(),
          adminApi.listProjects(),
        ])
        setUsers(userList)
        setActions(actionList)
        setProjects(projectList)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load overview')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [])

  const activeUsers = users.filter((u) => u.is_active).length
  const adminCount = users.filter((u) => u.is_admin).length

  const stats = [
    {
      label: 'Total users',
      value: loading ? '—' : String(users.length),
      icon: Users,
      hint: 'Accounts on this studio',
    },
    {
      label: 'Active',
      value: loading ? '—' : String(activeUsers),
      icon: UserCheck,
      hint: 'Can sign in today',
    },
    {
      label: 'Projects',
      value: loading ? '—' : String(projects.length),
      icon: FolderKanban,
      hint: 'User design sessions',
    },
    {
      label: 'Admins',
      value: loading ? '—' : String(adminCount),
      icon: Shield,
      hint: 'Full control access',
    },
    {
      label: 'Actions',
      value: loading ? '—' : String(actions.length),
      icon: Zap,
      hint: 'Assignable permissions',
    },
  ]

  return (
    <div className="admin-fade-in space-y-8">
      <header className="space-y-2">
        <p className="m-0 text-xs font-semibold uppercase tracking-[0.14em] text-primary">
          Administration
        </p>
        <h1 className="m-0 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Overview
        </h1>
        <p className="m-0 max-w-xl text-muted-text leading-relaxed">
          Manage who can use LabCD pipelines and which modules they can run.
        </p>
      </header>

      {error && <StatusMessage type="error" message={error} />}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {stats.map(({ label, value, icon: Icon, hint }) => (
          <div
            key={label}
            className={`${cardPanel} relative overflow-hidden transition-transform duration-200 hover:-translate-y-0.5`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-xs font-medium uppercase tracking-wide text-muted">
                  {label}
                </div>
                <div className="mt-2 text-3xl font-semibold tracking-tight text-foreground">
                  {value}
                </div>
                <div className="mt-1 text-sm text-muted-text">{hint}</div>
              </div>
              <div className="rounded-xl bg-[color-mix(in_srgb,var(--app-primary)_12%,transparent)] p-2.5 text-primary">
                <Icon className="size-5" aria-hidden />
              </div>
            </div>
          </div>
        ))}
      </div>

      <section className={`${cardPanel} flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between`}>
        <div>
          <h2 className="m-0 text-lg font-semibold text-foreground">Users & permissions</h2>
          <p className="mt-1 mb-0 text-sm text-muted-text leading-relaxed">
            Create accounts, set admin role, and assign Single Loop or Multi Loop action packs.
          </p>
        </div>
        <Link to="/admin/users" className={`${btnPrimary} shrink-0`}>
          <Users className="size-4" aria-hidden />
          Manage users
        </Link>
      </section>

      <section className={`${cardPanel} flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between`}>
        <div>
          <h2 className="m-0 text-lg font-semibold text-foreground">User projects</h2>
          <p className="mt-1 mb-0 text-sm text-muted-text leading-relaxed">
            Inspect uploaded dynamics files and design results across all user projects.
          </p>
        </div>
        <Link to="/admin/projects" className={`${btnPrimary} shrink-0`}>
          <FolderKanban className="size-4" aria-hidden />
          Manage projects
        </Link>
      </section>

      {!loading && actions.length > 0 && (
        <section className={cardPanel}>
          <h2 className="m-0 text-lg font-semibold text-foreground">Action catalog</h2>
          <p className="mt-1 mb-4 text-sm text-muted-text">
            Permissions you can grant when creating or editing a user.
          </p>
          <ul className="m-0 grid list-none gap-2 p-0 sm:grid-cols-2">
            {actions.map((action) => (
              <li
                key={action.code}
                className="rounded-lg border border-border-subtle bg-surface-muted px-3 py-2.5"
              >
                <div className="font-mono text-sm text-foreground">{action.code}</div>
                {action.description ? (
                  <div className="mt-0.5 text-xs text-muted-text">{action.description}</div>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
