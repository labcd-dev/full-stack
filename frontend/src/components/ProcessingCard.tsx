import { Loader2 } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

interface ProcessingCardProps {
  icon?: LucideIcon
  title: string
  description: string
}

export function ProcessingCard({ icon: Icon, title, description }: ProcessingCardProps) {
  return (
    <div className="processing-card setup-animate-in" role="status" aria-live="polite">
      <div className="processing-card__visual" aria-hidden>
        <span className="processing-card__ring processing-card__ring--outer" />
        <span className="processing-card__ring processing-card__ring--inner" />
        <span className="processing-card__core">
          {Icon ? (
            <Icon className="processing-card__core-icon" />
          ) : (
            <Loader2 className="processing-card__core-icon processing-card__core-icon--spin" />
          )}
        </span>
      </div>
      <h3 className="processing-card__title">{title}</h3>
      <p className="processing-card__description">{description}</p>
      <div className="processing-card__dots" aria-hidden>
        <span className="processing-card__dot" />
        <span className="processing-card__dot" />
        <span className="processing-card__dot" />
      </div>
    </div>
  )
}
