import { StatusLabel } from './StatusLabel'

interface ProgressBarProps {
  value: number
  label?: string
}

export function ProgressBar({ value, label }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, Math.round(value * 100)))

  return (
    <div className="my-4">
      {label && (
        <p className="m-0 mb-2 text-sm font-medium text-foreground">
          <StatusLabel text={label} />
        </p>
      )}
      <div className="h-2 bg-progress-track rounded-full overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-[width] duration-300 ease-out"
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      <span className="text-xs text-muted mt-1 inline-block tabular-nums">{pct}%</span>
    </div>
  )
}
