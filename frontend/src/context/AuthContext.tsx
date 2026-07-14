import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { authApi } from '../api/endpoints'
import { clearAuthToken, getAuthToken, setAuthToken } from '../api/client'
import type { AuthUser } from '../api/types'

interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  hasAction: (code: string) => boolean
  canUsePipeline: (pipeline: 'siloDesign' | 'muloDesign') => boolean
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

const PIPELINE_ACTION: Record<'siloDesign' | 'muloDesign', string> = {
  siloDesign: 'pipeline:silo',
  muloDesign: 'pipeline:mulo',
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [token, setToken] = useState<string | null>(() => getAuthToken())
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const current = getAuthToken()
    if (!current) {
      setUser(null)
      setToken(null)
      setLoading(false)
      return
    }
    try {
      const me = await authApi.me()
      setUser(me)
      setToken(current)
    } catch {
      clearAuthToken()
      setUser(null)
      setToken(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refreshUser()
  }, [refreshUser])

  const login = useCallback(async (email: string, password: string) => {
    const result = await authApi.login({ email, password })
    setAuthToken(result.access_token)
    setToken(result.access_token)
    const me = await authApi.me()
    setUser(me)
  }, [])

  const logout = useCallback(() => {
    clearAuthToken()
    setToken(null)
    setUser(null)
  }, [])

  const hasAction = useCallback(
    (code: string) => {
      if (!user) return false
      if (user.is_admin) return true
      return user.actions.includes(code)
    },
    [user],
  )

  const canUsePipeline = useCallback(
    (pipeline: 'siloDesign' | 'muloDesign') => hasAction(PIPELINE_ACTION[pipeline]),
    [hasAction],
  )

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      login,
      logout,
      hasAction,
      canUsePipeline,
      refreshUser,
    }),
    [user, token, loading, login, logout, hasAction, canUsePipeline, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
