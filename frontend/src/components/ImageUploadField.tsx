import { useRef, useState, type ChangeEvent } from 'react'
import { ImagePlus, Trash2, Upload } from 'lucide-react'
import { adminMediaApi } from '../api/endpoints'
import { btnBase, btnPrimary } from '../lib/classes'
import { StatusMessage } from './StatusMessage'

interface ImageUploadFieldProps {
  label: string
  value: string
  onChange: (url: string) => void
  prefix?: string
  hint?: string
  previewClassName?: string
}

export function ImageUploadField({
  label,
  value,
  onChange,
  prefix = 'image',
  hint = 'JPEG, PNG, WebP, GIF, or SVG up to 5 MB.',
  previewClassName = 'h-20 w-auto max-w-full object-contain',
}: ImageUploadFieldProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSelect = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return

    setError(null)
    setUploading(true)
    try {
      const uploaded = await adminMediaApi.upload(file, prefix)
      onChange(uploaded.url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload image')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-3">
      <p className="m-0 text-sm font-medium text-foreground">{label}</p>
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex min-h-20 min-w-28 items-center justify-center overflow-hidden rounded-lg border border-border bg-surface-muted px-3 py-2">
          {value ? (
            <img src={value} alt="" className={previewClassName} />
          ) : (
            <ImagePlus className="size-8 text-muted-text" aria-hidden />
          )}
        </div>
        <div className="space-y-2">
          <p className="m-0 text-sm text-muted-text">{hint}</p>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className={btnPrimary}
              disabled={uploading}
              onClick={() => inputRef.current?.click()}
            >
              <Upload className="size-4" aria-hidden />
              {uploading ? 'Uploading…' : value ? 'Replace image' : 'Upload image'}
            </button>
            {value && (
              <button
                type="button"
                className={btnBase}
                disabled={uploading}
                onClick={() => onChange('')}
              >
                <Trash2 className="size-4" aria-hidden />
                Remove
              </button>
            )}
          </div>
        </div>
      </div>
      {error && <StatusMessage type="error" message={error} />}
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif,image/svg+xml"
        className="hidden"
        onChange={(e) => void handleSelect(e)}
      />
    </div>
  )
}
