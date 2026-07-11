import type { LucideIcon } from 'lucide-react'
import { cleanStatusLabel, getStatusIcon } from '../lib/statusText'

interface StatusLabelProps {
  text: string
  icon?: LucideIcon
  className?: string
  iconClassName?: string
}

export function StatusLabel({
  text,
  icon,
  className = '',
  iconClassName = 'size-4 shrink-0 text-primary',
}: StatusLabelProps) {
  const Icon = icon ?? getStatusIcon(text)
  const label = cleanStatusLabel(text)

  return (
    <span className={`inline-flex items-center gap-2 min-w-0 ${className}`}>
      <Icon className={iconClassName} aria-hidden />
      <span className="truncate">{label}</span>
    </span>
  )
}
