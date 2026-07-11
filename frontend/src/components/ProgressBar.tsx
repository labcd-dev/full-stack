import { StatusLabel } from './StatusLabel'

interface ProgressBarProps {
  value: number
  label?: string
}

export function ProgressBar({ value, label }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, Math.round(value * 100)))
  const isComplete = pct >= 100
  const isActive = pct > 0 && !isComplete

  return (
    <div className="my-4">
      <div className="mb-2.5 flex items-center gap-3">
        {label && (
          <p className="m-0 min-w-0 flex-1 text-sm font-medium text-foreground">
            <StatusLabel text={label} />
          </p>
        )}
        <span
          className={`shrink-0 text-xs font-semibold tabular-nums text-foreground-secondary ${label ? '' : 'ml-auto'}`}
        >
          {pct}%
        </span>
      </div>
      <div
        className="progress-bar-track h-4 overflow-hidden rounded-full bg-progress-track"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className={[
            'progress-bar-fill h-full rounded-full',
            isActive && 'progress-bar-fill--active',
            isComplete && 'progress-bar-fill--complete',
          ]
            .filter(Boolean)
            .join(' ')}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
