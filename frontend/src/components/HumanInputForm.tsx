import { useState } from 'react'
import { btnBase, cardPanel, fieldInput } from '../lib/classes'

interface HumanInputFormProps {
  request: Record<string, unknown>
  onSubmit: (answer: string) => void
  disabled?: boolean
}

export function HumanInputForm({ request, onSubmit, disabled }: HumanInputFormProps) {
  const prompt = String(request.prompt ?? 'Please provide input')
  const options = parseOptions(String(request.options ?? ''))
  const [textAnswer, setTextAnswer] = useState('')

  if (options.length > 0) {
    return (
      <div className={`${cardPanel} mt-4`}>
        <p>{prompt}</p>
        <div className="flex flex-col gap-2">
          {options.map((option) => (
            <button
              key={option}
              type="button"
              className={btnBase}
              disabled={disabled}
              onClick={() => onSubmit(option)}
            >
              {option}
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <form
      className={`${cardPanel} mt-4 space-y-3`}
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit(textAnswer)
      }}
    >
      <p>{prompt}</p>
      <input
        type="text"
        className={fieldInput}
        value={textAnswer}
        onChange={(e) => setTextAnswer(e.target.value)}
        disabled={disabled}
      />
      <button type="submit" className={btnBase} disabled={disabled || !textAnswer.trim()}>
        Submit
      </button>
    </form>
  )
}

function parseOptions(raw: string): string[] {
  if (!raw) return []
  const match = raw.match(/\[(.*)\]/)
  if (!match) return []
  return match[1]
    .split(',')
    .map((item) => item.trim().replace(/^['"]|['"]$/g, ''))
    .filter(Boolean)
}
