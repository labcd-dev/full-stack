import type { LucideIcon } from 'lucide-react'
import {
  Activity,
  Bot,
  Brain,
  Eye,
  Globe,
  GraduationCap,
  Hourglass,
  Image,
  Layers,
  Palette,
  RefreshCw,
  Ruler,
  ScanEye,
  Search,
  Settings,
  UserCog,
  Wrench,
} from 'lucide-react'

const KEYWORD_ICONS: Array<{ pattern: RegExp; icon: LucideIcon }> = [
  { pattern: /parsing system/i, icon: Settings },
  { pattern: /standardiz/i, icon: Wrench },
  { pattern: /equation/i, icon: Ruler },
  { pattern: /system analysis|analyzing system/i, icon: Search },
  { pattern: /control loop structure|control loop analysis/i, icon: UserCog },
  { pattern: /control loop|standard format/i, icon: Layers },
  { pattern: /supervis|validat/i, icon: ScanEye },
  { pattern: /web search|searching web/i, icon: Globe },
  { pattern: /image recognition|block diagram|found block/i, icon: Image },
  { pattern: /human intervention|intervention/i, icon: Bot },
  { pattern: /strategy|planing/i, icon: Brain },
  { pattern: /solving equation/i, icon: GraduationCap },
  { pattern: /validate.*config|configue validator/i, icon: Hourglass },
  { pattern: /controller graph|creating controller/i, icon: Palette },
  { pattern: /equilibrium|analysing result/i, icon: ScanEye },
  { pattern: /executing/i, icon: Settings },
  { pattern: /recognition/i, icon: Eye },
  { pattern: /refresh|loop/i, icon: RefreshCw },
]

/** Strip emoji and mojibake prefixes from backend status strings. */
export function cleanStatusLabel(text: string): string {
  let cleaned = text.trim()
  cleaned = cleaned.replace(
    /^[\p{Extended_Pictographic}\p{Emoji_Presentation}\p{Emoji}\uFE0F\s]+/gu,
    '',
  )
  cleaned = cleaned.replace(/^(?:[\u0080-\u024F\u2000-\u206F\uFEFF]+[\.\s]*)+/u, '')
  cleaned = cleaned.replace(/^[^\w*]+[\.\s]*/, '')
  return cleaned.trim() || text.trim()
}

export function getStatusIcon(text: string): LucideIcon {
  const label = cleanStatusLabel(text)
  for (const { pattern, icon } of KEYWORD_ICONS) {
    if (pattern.test(label) || pattern.test(text)) return icon
  }
  return Activity
}
