const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
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
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...options.headers,
    },
  })

  if (!response.ok) {
    throw new ApiError(response.status, await parseError(response))
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export function artifactUrl(jobId: string, filename: string): string {
  return `${API_BASE}/jobs/${jobId}/artifacts/${encodeURIComponent(filename)}`
}

export function streamUrl(module: string, jobId: string): string {
  return `${API_BASE}/${module}/${jobId}/stream`
}
