import { Navigate } from 'react-router-dom'
import { useEffect, useMemo, useState, type FormEvent } from 'react'
import {
  Pencil,
  Plus,
  Search,
  Shield,
  UserPlus,
  X,
} from 'lucide-react'
import { adminApi } from '../api/endpoints'
import type { ActionInfo, AuthUser } from '../api/types'
import { StatusMessage } from '../components/StatusMessage'
import { useAuth } from '../context/AuthContext'
import {
  btnBase,
  btnCompact,
  btnPrimary,
  cardPanel,
  fieldCheckbox,
  fieldInput,
  fieldLabel,
} from '../lib/classes'

export function AdminUsersPage() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<AuthUser[]>([])
  const [actions, setActions] = useState<ActionInfo[]>([])
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [panelOpen, setPanelOpen] = useState(false)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isAdmin, setIsAdmin] = useState(false)
  const [selectedActions, setSelectedActions] = useState<string[]>([])
  const [editingUserId, setEditingUserId] = useState<number | null>(null)

  useEffect(() => {
    if (!currentUser?.is_admin) return
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const [userList, actionList] = await Promise.all([
          adminApi.listUsers(),
          adminApi.listActions(),
        ])
        setUsers(userList)
        setActions(actionList)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load users')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [currentUser?.is_admin])

  const filteredUsers = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return users
    return users.filter(
      (u) =>
        u.email.toLowerCase().includes(q) ||
        u.actions.some((a) => a.toLowerCase().includes(q)),
    )
  }, [users, query])

  if (!currentUser?.is_admin) {
    return <Navigate to="/" replace />
  }

  const toggleAction = (code: string) => {
    setSelectedActions((prev) =>
      prev.includes(code) ? prev.filter((item) => item !== code) : [...prev, code],
    )
  }

  const openCreate = () => {
    setEditingUserId(null)
    setEmail('')
    setPassword('')
    setIsAdmin(false)
    setSelectedActions([])
    setMessage(null)
    setError(null)
    setPanelOpen(true)
  }

  const startEdit = (user: AuthUser) => {
    setEditingUserId(user.id)
    setEmail(user.email)
    setPassword('')
    setIsAdmin(user.is_admin)
    setSelectedActions(user.actions)
    setMessage(null)
    setError(null)
    setPanelOpen(true)
  }

  const closePanel = () => {
    setPanelOpen(false)
    setEditingUserId(null)
    setEmail('')
    setPassword('')
    setIsAdmin(false)
    setSelectedActions([])
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setMessage(null)
    try {
      if (editingUserId == null) {
        await adminApi.createUser({
          email,
          password,
          is_admin: isAdmin,
          actions: selectedActions,
        })
        setMessage(`Created user ${email}`)
      } else {
        await adminApi.setUserActions(editingUserId, selectedActions)
        await adminApi.updateUser(editingUserId, {
          is_admin: isAdmin,
          ...(password ? { password } : {}),
        })
        setMessage(`Updated user ${email}`)
      }
      closePanel()
      const [userList, actionList] = await Promise.all([
        adminApi.listUsers(),
        adminApi.listActions(),
      ])
      setUsers(userList)
      setActions(actionList)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed')
    }
  }

  const quickAssign = (preset: 'silo' | 'mulo' | 'both') => {
    const silo = [
      'pipeline:silo',
      'module:upload',
      'module:regularize',
      'module:silo',
    ]
    const mulo = [
      'pipeline:mulo',
      'module:upload',
      'module:regularize',
      'module:recommender',
      'module:trimmer',
      'module:mulo',
      'module:case_studies',
    ]
    if (preset === 'silo') setSelectedActions(silo)
    else if (preset === 'mulo') setSelectedActions(mulo)
    else setSelectedActions([...new Set([...silo, ...mulo])])
  }

  return (
    <div className="admin-fade-in space-y-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-2">
          <p className="m-0 text-xs font-semibold uppercase tracking-[0.14em] text-primary">
            Access control
          </p>
          <h1 className="m-0 text-3xl font-semibold tracking-tight text-foreground">
            Users
          </h1>
          <p className="m-0 max-w-lg text-muted-text leading-relaxed">
            Create accounts by email and assign actions for Single Loop and Multi Loop.
          </p>
        </div>
        <button type="button" className={btnPrimary} onClick={openCreate}>
          <Plus className="size-4" aria-hidden />
          New user
        </button>
      </header>

      {error && !panelOpen && <StatusMessage type="error" message={error} />}
      {message && <StatusMessage type="success" message={message} />}

      <div className={`${cardPanel} space-y-4`}>
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted"
            aria-hidden
          />
          <input
            className={`${fieldInput} w-full pl-10`}
            type="search"
            placeholder="Search by email or action…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search users"
          />
        </div>

        {loading ? (
          <p className="py-8 text-center text-muted-text">Loading users…</p>
        ) : filteredUsers.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-12 text-center">
            <div className="rounded-2xl bg-surface-muted p-4 text-primary">
              <UserPlus className="size-8" aria-hidden />
            </div>
            <p className="m-0 font-medium text-foreground">
              {query ? 'No users match your search' : 'No users yet'}
            </p>
            <p className="m-0 text-sm text-muted-text">
              {query
                ? 'Try a different email or action code.'
                : 'Create the first account to grant pipeline access.'}
            </p>
            {!query && (
              <button type="button" className={btnPrimary} onClick={openCreate}>
                <Plus className="size-4" aria-hidden />
                New user
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-border-subtle">
            <table className="admin-users-table w-full min-w-[720px] border-collapse text-sm">
              <thead>
                <tr className="border-b border-border bg-surface-muted/80 text-left">
                  <th className="px-4 py-3 font-medium text-foreground-secondary">Email</th>
                  <th className="px-4 py-3 font-medium text-foreground-secondary">Role</th>
                  <th className="px-4 py-3 font-medium text-foreground-secondary">Status</th>
                  <th className="px-4 py-3 font-medium text-foreground-secondary">Permissions</th>
                  <th className="px-4 py-3 font-medium text-foreground-secondary">Created</th>
                  <th className="px-4 py-3 text-right font-medium text-foreground-secondary">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr
                    key={user.id}
                    className="border-b border-border-subtle transition-colors last:border-b-0 hover:bg-surface-hover/50"
                  >
                    <td className="px-4 py-3 font-medium text-foreground">{user.email}</td>
                    <td className="px-4 py-3">
                      {user.is_admin ? (
                        <span className="inline-flex items-center gap-1 rounded-md bg-[color-mix(in_srgb,var(--app-primary)_14%,transparent)] px-2 py-0.5 text-xs font-semibold text-primary">
                          <Shield className="size-3" aria-hidden />
                          Admin
                        </span>
                      ) : (
                        <span className="rounded-md bg-surface-elevated px-2 py-0.5 text-xs font-medium text-muted-text ring-1 ring-border">
                          User
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {user.is_active ? (
                        <span className="rounded-md bg-[var(--app-status-success-bg)] px-2 py-0.5 text-xs font-medium text-[var(--app-status-success-text)]">
                          Active
                        </span>
                      ) : (
                        <span className="rounded-md bg-[var(--app-status-warning-bg)] px-2 py-0.5 text-xs font-medium text-[var(--app-status-warning-text)]">
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {user.actions.length === 0 ? (
                        <span className="text-muted-text">None</span>
                      ) : (
                        <div className="flex max-w-md flex-wrap gap-1.5">
                          {user.actions.map((code) => (
                            <span
                              key={code}
                              className="rounded-md bg-surface-elevated px-1.5 py-0.5 font-mono text-[0.68rem] text-foreground-secondary ring-1 ring-border-subtle"
                            >
                              {code}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-muted-text">
                      {new Date(user.created_at).toLocaleDateString(undefined, {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        type="button"
                        className={`${btnBase} ${btnCompact}`}
                        onClick={() => startEdit(user)}
                      >
                        <Pencil className="size-3.5" aria-hidden />
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {panelOpen && (
        <>
          <button
            type="button"
            className="admin-fade-in fixed inset-0 z-40 bg-foreground/35 backdrop-blur-[2px]"
            aria-label="Close panel"
            onClick={closePanel}
          />
          <aside
            className="admin-slide-in fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col border-l border-border bg-surface-elevated shadow-2xl"
            role="dialog"
            aria-modal="true"
            aria-labelledby="admin-user-panel-title"
          >
            <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-4">
              <h2
                id="admin-user-panel-title"
                className="m-0 text-lg font-semibold text-foreground"
              >
                {editingUserId == null ? 'Create user' : 'Edit user'}
              </h2>
              <button
                type="button"
                className={`${btnBase} ${btnCompact}`}
                onClick={closePanel}
                aria-label="Close"
              >
                <X className="size-4" />
              </button>
            </div>

            <form
              onSubmit={(e) => void handleSubmit(e)}
              className="flex min-h-0 flex-1 flex-col"
            >
              <div className="flex-1 space-y-1 overflow-y-auto px-5 py-4">
                {error && <StatusMessage type="error" message={error} />}

                <label className={fieldLabel}>
                  <span>Email</span>
                  <input
                    className={fieldInput}
                    type="email"
                    required
                    disabled={editingUserId != null}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </label>
                <label className={fieldLabel}>
                  <span>{editingUserId == null ? 'Password' : 'New password (optional)'}</span>
                  <input
                    className={fieldInput}
                    type="password"
                    minLength={6}
                    required={editingUserId == null}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </label>
                <label className={fieldCheckbox}>
                  <input
                    type="checkbox"
                    checked={isAdmin}
                    onChange={(e) => setIsAdmin(e.target.checked)}
                  />
                  <span>Admin privileges</span>
                </label>

                <div className="mb-3">
                  <div className="mb-2 text-sm font-medium text-foreground">Quick assign</div>
                  <div className="flex flex-wrap gap-2">
                    <button type="button" className={`${btnBase} ${btnCompact}`} onClick={() => quickAssign('silo')}>
                      Single Loop
                    </button>
                    <button type="button" className={`${btnBase} ${btnCompact}`} onClick={() => quickAssign('mulo')}>
                      Multi Loop
                    </button>
                    <button type="button" className={`${btnBase} ${btnCompact}`} onClick={() => quickAssign('both')}>
                      Both
                    </button>
                  </div>
                </div>

                <fieldset className="mb-2 space-y-2 border-0 p-0">
                  <legend className="mb-2 text-sm font-medium text-foreground">Actions</legend>
                  <div className="max-h-56 space-y-1 overflow-y-auto rounded-xl border border-border p-2">
                    {actions.map((action) => {
                      const checked = selectedActions.includes(action.code)
                      return (
                        <label
                          key={action.code}
                          className={`flex cursor-pointer items-start gap-2.5 rounded-lg px-2.5 py-2 transition-colors ${
                            checked
                              ? 'bg-[color-mix(in_srgb,var(--app-primary)_10%,transparent)]'
                              : 'hover:bg-surface-hover'
                          }`}
                        >
                          <input
                            type="checkbox"
                            className="mt-1"
                            checked={checked}
                            onChange={() => toggleAction(action.code)}
                          />
                          <span>
                            <span className="block font-mono text-sm text-foreground">
                              {action.code}
                            </span>
                            {action.description ? (
                              <span className="text-xs text-muted-text">{action.description}</span>
                            ) : null}
                          </span>
                        </label>
                      )
                    })}
                  </div>
                </fieldset>
              </div>

              <div className="flex flex-wrap gap-2 border-t border-border px-5 py-4">
                <button type="submit" className={btnPrimary}>
                  {editingUserId == null ? 'Create user' : 'Save changes'}
                </button>
                <button type="button" className={btnBase} onClick={closePanel}>
                  Cancel
                </button>
              </div>
            </form>
          </aside>
        </>
      )}
    </div>
  )
}
