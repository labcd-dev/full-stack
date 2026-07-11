import { useMemo } from 'react'
import type { StreamEvent } from '../api/types'

function latestMonitorFromEvents(events: StreamEvent[]): Record<string, unknown> | null {
  for (let index = events.length - 1; index >= 0; index -= 1) {
    const event = events[index]
    if (
      (event.type === 'monitor' || event.type === 'monitor_update') &&
      event.content &&
      typeof event.content === 'object'
    ) {
      return event.content as Record<string, unknown>
    }
  }
  return null
}

export function useMonitorState(
  pollData: Record<string, unknown> | null | undefined,
  streamEvents: StreamEvent[],
): Record<string, unknown> | null {
  const streamSnapshot = useMemo(
    () => latestMonitorFromEvents(streamEvents),
    [streamEvents],
  )

  return streamSnapshot ?? pollData ?? null
}
