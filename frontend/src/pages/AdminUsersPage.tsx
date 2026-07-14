import { Navigate } from 'react-router-dom'
import { useEffect, useState, type FormEvent } from 'react'
import { adminApi } from '../api/endpoints'
import type { ActionInfo, AuthUser } from '../api/types'
import { StatusMessage } from '../components/StatusMessage'
import { useAuth } from '../context/AuthContext'
import {
  btnBase,
  btnPrimary,
  cardPanel,
  fieldCheckbox,
  fieldInput,
  fieldLabel,
  pageIntro,
  pageSection,
} from '../lib/classes'

export function AdminUsersPage() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<AuthUser[]>([])
  const [actions, setActions] = useState<ActionInfo[]>([])
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

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

  if (!currentUser?.is_admin) {
    return <Navigate to="/" replace />
  }

  const toggleAction = (code: string) => {
    setSelectedActions((prev) =>
      prev.includes(code) ? prev.filter((item) => item !== code) : [...prev, code],
    )
  }

  const startEdit = (user: AuthUser) => {
    setEditingUserId(user.id)
    setEmail(user.email)
    setPassword('')
    setIsAdmin(user.is_admin)
    setSelectedActions(user.actions)
    setMessage(null)
  }

  const resetForm = () => {
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
      resetForm()
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
    <section className={pageSection}>
      <header>
        <h2 className="m-0 text-2xl font-semibold tracking-tight text-foreground">Users & actions</h2>
        <p className={pageIntro}>
          Create users by email and assign any actions so they can run Single Loop and/or Multi Loop
          for themselves.
        </p>
      </header>

      {error && <StatusMessage type="error" message={error} />}
      {message && <StatusMessage type="success" message={message} />}

      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <div className={`${cardPanel} space-y-3`}>
          <h3 className="m-0 text-base font-semibold text-foreground">
            {editingUserId == null ? 'Create user' : 'Edit user'}
          </h3>
          <form onSubmit={(e) => void handleSubmit(e)} className="space-y-1">
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
              <span>Admin</span>
            </label>

            <div className="mb-3 flex flex-wrap gap-2">
              <button type="button" className={btnBase} onClick={() => quickAssign('silo')}>
                Single Loop pack
              </button>
              <button type="button" className={btnBase} onClick={() => quickAssign('mulo')}>
                Multi Loop pack
              </button>
              <button type="button" className={btnBase} onClick={() => quickAssign('both')}>
                Both pipelines
              </button>
            </div>

            <fieldset className="mb-4 space-y-2">
              <legend className="mb-2 text-sm font-medium text-foreground">Actions</legend>
              <div className="max-h-64 space-y-2 overflow-y-auto rounded-lg border border-border p-3">
                {actions.map((action) => (
                  <label key={action.code} className={fieldCheckbox}>
                    <input
                      type="checkbox"
                      checked={selectedActions.includes(action.code)}
                      onChange={() => toggleAction(action.code)}
                    />
                    <span>
                      <span className="font-mono text-sm">{action.code}</span>
                      {action.description ? (
                        <span className="ml-2 text-muted-text">{action.description}</span>
                      ) : null}
                    </span>
                  </label>
                ))}
              </div>
            </fieldset>

            <div className="flex flex-wrap gap-2">
              <button type="submit" className={btnPrimary}>
                {editingUserId == null ? 'Create user' : 'Save changes'}
              </button>
              {editingUserId != null && (
                <button type="button" className={btnBase} onClick={resetForm}>
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>

        <div className={`${cardPanel} space-y-3`}>
          <h3 className="m-0 text-base font-semibold text-foreground">Existing users</h3>
          {loading ? (
            <p className="text-muted-text">Loading…</p>
          ) : (
            <ul className="m-0 space-y-2 p-0 list-none">
              {users.map((user) => (
                <li
                  key={user.id}
                  className="rounded-lg border border-border-subtle bg-surface-muted px-3 py-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="font-medium text-foreground">{user.email}</div>
                      <div className="text-xs text-muted-text">
                        {user.is_admin ? 'Admin' : 'User'}
                        {!user.is_active ? ' · inactive' : ''}
                        {' · '}
                        {user.actions.length} action{user.actions.length === 1 ? '' : 's'}
                      </div>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {user.actions.map((code) => (
                          <span
                            key={code}
                            className="rounded bg-surface-hover px-1.5 py-0.5 font-mono text-[0.7rem] text-foreground-secondary"
                          >
                            {code}
                          </span>
                        ))}
                      </div>
                    </div>
                    <button type="button" className={btnBase} onClick={() => startEdit(user)}>
                      Edit
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  )
}
