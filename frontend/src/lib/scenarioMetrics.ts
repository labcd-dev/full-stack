/** Types and display helpers for SILO Computational Profiling metrics. */

export interface ScenarioMetrics {
  tokens_in?: number
  tokens_out?: number
  time?: number
  cost?: number
  api_failures?: number
  stable?: boolean
  score?: number
  cost_per_success?: number | null
  controller_latency_s?: number
  controller_type?: string | null
}

export interface ScenarioMetricsEntry {
  scenario_level: number
  timestamp?: string
  metrics: ScenarioMetrics
}

export interface SessionProfilingSummary {
  nSuccessful: number
  nTotal: number
  avgSuccessScore: number
  totalApiFails: number
  avgCostPerSuccess: number | null
  totalTokensIn: number
  totalTokensOut: number
  totalTime: number
  totalCost: number
}

export interface DevOpsKpiRow {
  level: number
  controller: string
  stable: boolean
  score: number
  latency: number
  apiFails: number
  costPerSuccess: number | null
}

export interface TokenCostRow {
  level: number
  tokensIn: number
  tokensOut: number
  time: number
  cost: number
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

function parseMetrics(raw: unknown): ScenarioMetrics {
  const m = asRecord(raw) ?? {}
  const cps = m.cost_per_success
  return {
    tokens_in: asNumber(m.tokens_in),
    tokens_out: asNumber(m.tokens_out),
    time: asNumber(m.time),
    cost: asNumber(m.cost),
    api_failures: asNumber(m.api_failures),
    stable: Boolean(m.stable),
    score: asNumber(m.score),
    cost_per_success:
      cps === null || cps === undefined
        ? null
        : typeof cps === 'number' && Number.isFinite(cps)
          ? cps
          : null,
    controller_latency_s:
      typeof m.controller_latency_s === 'number' && Number.isFinite(m.controller_latency_s)
        ? m.controller_latency_s
        : undefined,
    controller_type:
      typeof m.controller_type === 'string' && m.controller_type
        ? m.controller_type
        : null,
  }
}

/** Parse monitor `scenario_metrics_history` into typed entries. */
export function parseScenarioMetricsHistory(value: unknown): ScenarioMetricsEntry[] {
  if (!Array.isArray(value)) return []
  const entries: ScenarioMetricsEntry[] = []
  for (const item of value) {
    const record = asRecord(item)
    if (!record) continue
    const level = asNumber(record.scenario_level, NaN)
    if (!Number.isFinite(level)) continue
    entries.push({
      scenario_level: level,
      timestamp: typeof record.timestamp === 'string' ? record.timestamp : undefined,
      metrics: parseMetrics(record.metrics),
    })
  }
  return entries
}

/** Session-level aggregates matching Streamlit `display_current_metrics`. */
export function buildSessionProfilingSummary(
  history: ScenarioMetricsEntry[],
): SessionProfilingSummary {
  const nTotal = history.length
  const totalTokensIn = history.reduce((sum, e) => sum + (e.metrics.tokens_in ?? 0), 0)
  const totalTokensOut = history.reduce((sum, e) => sum + (e.metrics.tokens_out ?? 0), 0)
  const totalTime = history.reduce((sum, e) => sum + (e.metrics.time ?? 0), 0)
  const totalCost = history.reduce((sum, e) => sum + (e.metrics.cost ?? 0), 0)
  const totalApiFails = history.reduce((sum, e) => sum + (e.metrics.api_failures ?? 0), 0)
  const nSuccessful = history.filter((e) => e.metrics.stable).length
  const successfulCosts = history
    .map((e) => e.metrics.cost_per_success)
    .filter((c): c is number => c !== null && c !== undefined)
  const avgCostPerSuccess =
    successfulCosts.length > 0
      ? successfulCosts.reduce((a, b) => a + b, 0) / successfulCosts.length
      : null
  const avgSuccessScore =
    nTotal > 0
      ? history.reduce((sum, e) => sum + (e.metrics.score ?? 0), 0) / nTotal
      : 0

  return {
    nSuccessful,
    nTotal,
    avgSuccessScore,
    totalApiFails,
    avgCostPerSuccess,
    totalTokensIn,
    totalTokensOut,
    totalTime,
    totalCost,
  }
}

export function buildDevOpsKpiRows(history: ScenarioMetricsEntry[]): DevOpsKpiRow[] {
  return history.map((entry) => {
    const m = entry.metrics
    return {
      level: entry.scenario_level,
      controller: m.controller_type || '—',
      stable: Boolean(m.stable),
      score: m.score ?? 0,
      latency: m.controller_latency_s ?? m.time ?? 0,
      apiFails: m.api_failures ?? 0,
      costPerSuccess: m.cost_per_success ?? null,
    }
  })
}

export function buildTokenCostRows(history: ScenarioMetricsEntry[]): TokenCostRow[] {
  return history.map((entry) => ({
    level: entry.scenario_level,
    tokensIn: entry.metrics.tokens_in ?? 0,
    tokensOut: entry.metrics.tokens_out ?? 0,
    time: entry.metrics.time ?? 0,
    cost: entry.metrics.cost ?? 0,
  }))
}

export function formatScorePercent(score: number): string {
  return `${Math.round(score * 100)}%`
}

export function formatCost(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return `$${value.toFixed(4)}`
}

export function formatSeconds(value: number): string {
  return `${value.toFixed(1)}s`
}
