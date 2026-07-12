import { Check, Cpu, Rocket, Sparkles, Upload } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { cardPanel } from '../lib/classes'

export type SetupStage = 'upload' | 'processing' | 'result' | 'standardizing' | 'ready'

interface StepDef {
  id: string
  label: string
  description: string
  icon: LucideIcon
}

const STEPS: StepDef[] = [
  { id: 'upload', label: 'Upload', description: 'System file', icon: Upload },
  { id: 'process', label: 'Process', description: 'Syntax check', icon: Cpu },
  { id: 'standardize', label: 'Standardize', description: 'Format code', icon: Sparkles },
  { id: 'ready', label: 'Launch', description: 'Start design', icon: Rocket },
]

function stageToIndex(stage: SetupStage): number {
  switch (stage) {
    case 'upload':
      return 0
    case 'processing':
    case 'result':
      return 1
    case 'standardizing':
      return 2
    case 'ready':
      return 3
    default:
      return 0
  }
}

interface SetupStepIndicatorProps {
  stage: SetupStage
}

export function SetupStepIndicator({ stage }: SetupStepIndicatorProps) {
  const activeIndex = stageToIndex(stage)

  return (
    <div className={`${cardPanel} setup-steps-card setup-animate-in`}>
      <nav className="setup-steps" aria-label="Setup progress">
        <ol className="setup-steps__list">
        {STEPS.map((step, index) => {
          const Icon = step.icon
          const isComplete = index < activeIndex
          const isActive = index === activeIndex
          const isPending = index > activeIndex

          return (
            <li
              key={step.id}
              className={[
                'setup-steps__item',
                isComplete && 'setup-steps__item--complete',
                isActive && 'setup-steps__item--active',
                isPending && 'setup-steps__item--pending',
              ]
                .filter(Boolean)
                .join(' ')}
              aria-current={isActive ? 'step' : undefined}
            >
              {index > 0 && (
                <span
                  className={[
                    'setup-steps__connector',
                    isComplete && 'setup-steps__connector--complete',
                  ]
                    .filter(Boolean)
                    .join(' ')}
                  aria-hidden
                />
              )}
              <div className="setup-steps__node">
                <span className="setup-steps__icon-wrap">
                  {isComplete ? (
                    <Check className="setup-steps__icon" aria-hidden />
                  ) : (
                    <Icon className="setup-steps__icon" aria-hidden />
                  )}
                </span>
                <span className="setup-steps__label">{step.label}</span>
                <span className="setup-steps__description">{step.description}</span>
              </div>
            </li>
          )
        })}
        </ol>
      </nav>
    </div>
  )
}
