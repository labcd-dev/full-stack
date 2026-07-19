import { useEffect } from 'react'
import { BrainCircuit } from 'lucide-react'
import { fieldInput, fieldLabel } from '../lib/classes'

interface ModelSelectProps {
  models: string[]
  value: string
  onChange: (model: string) => void
  label?: string
}

export function ModelSelect({ models, value, onChange, label = 'LLM Model' }: ModelSelectProps) {
  useEffect(() => {
    if (models.length > 0 && !models.includes(value)) {
      onChange(models[0])
    }
  }, [models, value, onChange])

  return (
    <label className={fieldLabel}>
      <span className="inline-flex items-center gap-1.5">
        <BrainCircuit className="size-4 text-primary" aria-hidden />
        {label}
      </span>
      <select className={fieldInput} value={value} onChange={(e) => onChange(e.target.value)}>
        {models.map((model) => (
          <option key={model} value={model}>
            {model}
          </option>
        ))}
      </select>
    </label>
  )
}
