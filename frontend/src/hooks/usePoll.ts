import { useEffect, useState } from 'react'

export function usePoll<T>(
  fetcher: () => Promise<T>,
  intervalMs: number,
  enabled = true,
) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!enabled) return

    let active = true

    const poll = async () => {
      try {
        const result = await fetcher()
        if (active) {
          setData(result)
          setError(null)
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : String(err))
        }
      }
    }

    poll()
    const timer = window.setInterval(poll, intervalMs)
    return () => {
      active = false
      window.clearInterval(timer)
    }
  }, [fetcher, intervalMs, enabled])

  return { data, error }
}
