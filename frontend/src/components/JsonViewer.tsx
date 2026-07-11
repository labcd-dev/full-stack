import { cardPanel, logPre } from '../lib/classes'

interface JsonViewerProps {
  data: unknown
  title?: string
}

export function JsonViewer({ data, title }: JsonViewerProps) {
  return (
    <details className={`${cardPanel} p-3 mb-3 text-foreground`} open={!title}>
      {title && <summary className="cursor-pointer">{title}</summary>}
      <pre className={logPre}>{JSON.stringify(data, null, 2)}</pre>
    </details>
  )
}
