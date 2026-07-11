import { Activity } from 'lucide-react'
import { cardPanel, logPre, mutedText } from '../lib/classes'
import { StatusLabel } from './StatusLabel'

interface ActivityLogProps {
  logs: Array<Record<string, unknown>>
}

export function ActivityLog({ logs }: ActivityLogProps) {
  if (logs.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-8 text-center">
        <Activity className="size-8 text-foreground-faint" aria-hidden />
        <p className={mutedText}>No activity yet.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      {logs.map((log, index) => (
        <div key={index} className={`${cardPanel} p-4`}>
          {typeof log.agent_tag === 'string' && (
            <div className="font-semibold text-foreground mb-1">
              <StatusLabel text={log.agent_tag} iconClassName="size-4 shrink-0 text-primary" />
            </div>
          )}
          <pre className={logPre}>{formatLogContent(log.log_history ?? log)}</pre>
        </div>
      ))}
    </div>
  )
}

function formatLogContent(content: unknown): string {
  if (typeof content === 'string') return content
  return JSON.stringify(content, null, 2)
}
