import { Download } from 'lucide-react'
import { btnBase, btnCompact, btnPrimary } from '../../lib/classes'

type AdminDownloadCsvButtonProps = {
  onClick: () => void | Promise<void>
  disabled?: boolean
  primary?: boolean
  label?: string
}

export function AdminDownloadCsvButton({
  onClick,
  disabled,
  primary = false,
  label = 'Download CSV',
}: AdminDownloadCsvButtonProps) {
  return (
    <button
      type="button"
      className={`${btnBase} ${primary ? btnPrimary : ''} ${btnCompact}`}
      onClick={() => void onClick()}
      disabled={disabled}
    >
      <Download className="size-3.5" aria-hidden />
      {label}
    </button>
  )
}
