import { Gauge, Network } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

type Pipeline = 'siloDesign' | 'muloDesign'

interface PipelineOption {
  id: Pipeline
  title: string
  description: string
  icon: LucideIcon
}

const PIPELINES: PipelineOption[] = [
  {
    id: 'siloDesign',
    title: 'Single Loop',
    description: 'Design one control loop with the Silo Designer pipeline.',
    icon: Gauge,
  },
  {
    id: 'muloDesign',
    title: 'Multi Loop',
    description: 'Coordinate multiple loops via Recommender, Trimmer, and MULO.',
    icon: Network,
  },
]

interface PipelineSelectorProps {
  value: Pipeline | null
  onChange: (pipeline: Pipeline) => void
}

export function PipelineSelector({ value, onChange }: PipelineSelectorProps) {
  return (
    <fieldset className="pipeline-selector">
      <legend className="pipeline-selector__legend">Design pipeline</legend>
      <div className="pipeline-selector__grid">
        {PIPELINES.map((option) => {
          const Icon = option.icon
          const isSelected = value === option.id

          return (
            <button
              key={option.id}
              type="button"
              className={[
                'pipeline-card',
                isSelected && 'pipeline-card--selected',
              ]
                .filter(Boolean)
                .join(' ')}
              onClick={() => onChange(option.id)}
              aria-pressed={isSelected}
            >
              <span className="pipeline-card__icon-wrap" aria-hidden>
                <Icon className="pipeline-card__icon" />
              </span>
              <span className="pipeline-card__content">
                <span className="pipeline-card__title">{option.title}</span>
                <span className="pipeline-card__description">{option.description}</span>
              </span>
              <span className="pipeline-card__check" aria-hidden>
                <span className="pipeline-card__check-dot" />
              </span>
            </button>
          )
        })}
      </div>
    </fieldset>
  )
}
