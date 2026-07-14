const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'
const TOKEN_KEY = 'labcd_access_token'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setAuthToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearAuthToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

async function parseError(response: Response): Promise<string> {
  try {
    const body = await response.json()
    return body.detail ?? body.message ?? response.statusText
  } catch {
    return response.statusText
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getAuthToken()
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  if (response.status === 401 && !path.startsWith('/auth/login')) {
    clearAuthToken()
  }

  if (!response.ok) {
    throw new ApiError(response.status, await parseError(response))
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export function artifactUrl(jobId: string, filename: string): string {
  const token = getAuthToken()
  const base = `${API_BASE}/jobs/${jobId}/artifacts/${encodeURIComponent(filename)}`
  return token ? `${base}?access_token=${encodeURIComponent(token)}` : base
}

export function streamUrl(module: string, jobId: string): string {
  const token = getAuthToken()
  const base = `${API_BASE}/${module}/${jobId}/stream`
  return token ? `${base}?access_token=${encodeURIComponent(token)}` : base
}
