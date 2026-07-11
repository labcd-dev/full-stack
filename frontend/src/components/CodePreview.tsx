import { codePreview } from '../lib/classes'

interface CodePreviewProps {
  value: string
  onChange?: (value: string) => void
  readOnly?: boolean
  height?: number
}

export function CodePreview({
  value,
  onChange,
  readOnly = false,
  height = 400,
}: CodePreviewProps) {
  return (
    <textarea
      className={codePreview}
      value={value}
      readOnly={readOnly || !onChange}
      onChange={(e) => onChange?.(e.target.value)}
      style={{ height }}
      spellCheck={false}
    />
  )
}
