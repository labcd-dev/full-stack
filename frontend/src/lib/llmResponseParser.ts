export interface LlmResponseEntry {
  timestamp?: string
  agent?: string
  role?: string
  prompt?: string
  response?: string
  content?: string
}

export interface ParsedActor {
  params: Record<string, number | string>
  reasoning?: string
}

export interface ParsedCritic {
  strategy?: string
  result_analysis?: string
  suggested_improvements?: string[]
}

export interface ParsedTerminator {
  decision?: string
  reasoning?: string
  recommendations?: string
}

export interface AgentResponse<T> {
  raw: LlmResponseEntry
  parsed: T
}

export interface IterationCycle {
  iteration: number
  timestamp?: string
  actor?: AgentResponse<ParsedActor>
  critic?: AgentResponse<ParsedCritic>
  terminator?: AgentResponse<ParsedTerminator>
  juror?: AgentResponse<Record<string, unknown>>
}

const ACTOR_PARAM_KEYS = new Set(['reasoning'])
const KNOWN_AGENTS = new Set(['LLMActor', 'LLMCritic', 'LLMTerminator', 'LLMJuror'])

export function normalizeAgentName(agent?: string): string {
  if (!agent) return 'Unknown'
  const trimmed = agent.trim()
  if (KNOWN_AGENTS.has(trimmed)) return trimmed
  if (trimmed.toLowerCase().includes('actor')) return 'LLMActor'
  if (trimmed.toLowerCase().includes('critic')) return 'LLMCritic'
  if (trimmed.toLowerCase().includes('terminator')) return 'LLMTerminator'
  if (trimmed.toLowerCase().includes('juror')) return 'LLMJuror'
  return trimmed
}

export function getResponseText(entry: LlmResponseEntry): string {
  return String(entry.response ?? entry.content ?? '')
}

export function extractJsonFromResponse(text: string): Record<string, unknown> | null {
  const cleaned = text.replace(/[\s\S]*?<\/think>/gi, '').trim()
  if (!cleaned) return null

  const fenced = cleaned.match(/```(?:json)?\s*([\s\S]*?)```/i)
  const candidate = fenced ? fenced[1].trim() : cleaned

  const start = candidate.indexOf('{')
  const end = candidate.lastIndexOf('}')
  if (start === -1 || end === -1 || end <= start) return null

  try {
    const parsed = JSON.parse(candidate.slice(start, end + 1))
    return typeof parsed === 'object' && parsed !== null ? (parsed as Record<string, unknown>) : null
  } catch {
    return null
  }
}

export function parseActorResponse(text: string): ParsedActor {
  const data = extractJsonFromResponse(text)
  if (!data) return { params: {}, reasoning: text.trim() || undefined }

  const params: Record<string, number | string> = {}
  for (const [key, value] of Object.entries(data)) {
    if (ACTOR_PARAM_KEYS.has(key)) continue
    if (typeof value === 'number' || typeof value === 'string') {
      params[key] = value
    }
  }

  return {
    params,
    reasoning: typeof data.reasoning === 'string' ? data.reasoning : undefined,
  }
}

export function parseCriticResponse(text: string): ParsedCritic {
  const data = extractJsonFromResponse(text)
  if (!data) return { result_analysis: text.trim() || undefined }

  const improvements = data.suggested_improvements
  return {
    strategy: typeof data.strategy === 'string' ? data.strategy : undefined,
    result_analysis:
      typeof data.result_analysis === 'string' ? data.result_analysis : undefined,
    suggested_improvements: Array.isArray(improvements)
      ? improvements.filter((item): item is string => typeof item === 'string')
      : undefined,
  }
}

export function parseTerminatorResponse(text: string): ParsedTerminator {
  const data = extractJsonFromResponse(text)
  if (!data) return { reasoning: text.trim() || undefined }

  return {
    decision: typeof data.decision === 'string' ? data.decision : undefined,
    reasoning: typeof data.reasoning === 'string' ? data.reasoning : undefined,
    recommendations:
      typeof data.recommendations === 'string' ? data.recommendations : undefined,
  }
}

export function groupIntoIterations(responses: LlmResponseEntry[]): IterationCycle[] {
  const cycles: IterationCycle[] = []
  let current: IterationCycle | null = null
  let iterationNum = 0

  for (const entry of responses) {
    const agent = normalizeAgentName(
      typeof entry.agent === 'string' ? entry.agent : String(entry.role ?? ''),
    )
    const text = getResponseText(entry)

    if (agent === 'LLMActor') {
      if (current) cycles.push(current)
      iterationNum += 1
      current = {
        iteration: iterationNum,
        timestamp: typeof entry.timestamp === 'string' ? entry.timestamp : undefined,
        actor: { raw: entry, parsed: parseActorResponse(text) },
      }
      continue
    }

    if (!current) continue

    if (agent === 'LLMCritic') {
      current.critic = { raw: entry, parsed: parseCriticResponse(text) }
    } else if (agent === 'LLMTerminator') {
      current.terminator = { raw: entry, parsed: parseTerminatorResponse(text) }
    } else if (agent === 'LLMJuror') {
      current.juror = {
        raw: entry,
        parsed: extractJsonFromResponse(text) ?? { raw: text },
      }
    }
  }

  if (current) cycles.push(current)
  return cycles
}

export function formatParamValue(value: number | string): string {
  if (typeof value === 'number') {
    return Number.isInteger(value) ? String(value) : value.toFixed(4)
  }
  return value
}
