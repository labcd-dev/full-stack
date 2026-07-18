import type { Data, Layout } from 'plotly.js'
import type { MuloPlotData } from './muloDesignConfig'

const BLUE = '#2196F3'
const RED = '#F44336'
const GREEN = '#4CAF50'
const ORANGE = '#FF9800'
const PURPLE = '#9C27B0'
const TEAL = '#00BCD4'
const GRAY = 'rgba(120,120,120,0.55)'
const RANGE_FILL = 'rgba(33,150,243,0.13)'

function attemptNfeExtents(pd: MuloPlotData): Record<number, { nfe_min: number; nfe_max: number }> {
  const extents: Record<number, { nfe_min: number; nfe_max: number }> = {}
  pd.cumulative_nfe.forEach((nfe, index) => {
    const att = pd.attempt[index]
    if (!(att in extents)) {
      extents[att] = { nfe_min: nfe, nfe_max: nfe }
    } else {
      extents[att].nfe_max = Math.max(extents[att].nfe_max, nfe)
    }
  })
  return extents
}

export function buildCostChart(pd: MuloPlotData): { data: Data[]; layout: Partial<Layout> } {
  const shapes = pd.attempt_boundaries_nfe.map((nfe) => ({
    type: 'line' as const,
    x0: nfe,
    x1: nfe,
    y0: 0,
    y1: 1,
    yref: 'paper' as const,
    line: { dash: 'dash' as const, color: GRAY, width: 1 },
  }))

  return {
    data: [
      {
        x: pd.cumulative_nfe,
        y: pd.best_baseline_so_far,
        type: 'scatter',
        mode: 'lines',
        name: 'Best Baseline Cost',
        line: { color: BLUE, width: 2.5 },
      },
    ],
    layout: {
      title: { text: 'Best Baseline Cost vs Cumulative NFE' },
      xaxis: { title: { text: 'Cumulative NFE' } },
      yaxis: { title: { text: 'Best Baseline Cost' } },
      shapes: [
        ...shapes,
        {
          type: 'line',
          x0: 0,
          x1: 1,
          xref: 'paper',
          y0: 0,
          y1: 0,
          line: { dash: 'dash', color: GREEN, width: 1 },
        },
      ],
      height: 300,
    },
  }
}

export function buildMetricsCharts(
  pd: MuloPlotData,
  targets: Record<string, number> = {},
): { data: Data[]; layout: Partial<Layout> }[] {
  const metrics = [
    { key: 'mse', label: 'MSE', color: BLUE },
    { key: 'settling_time', label: 'Settling Time', color: ORANGE },
    { key: 'overshoot', label: 'Overshoot', color: PURPLE },
    { key: 'control_effort', label: 'Control Effort', color: TEAL },
  ] as const

  return metrics.map(({ key, label, color }) => {
    const target = targets[key]
    const shapes = [
      ...pd.attempt_boundaries_nfe.map((nfe) => ({
        type: 'line' as const,
        x0: nfe,
        x1: nfe,
        y0: 0,
        y1: 1,
        yref: 'paper' as const,
        line: { dash: 'dash' as const, color: GRAY, width: 1 },
      })),
      ...(target !== undefined
        ? [
            {
              type: 'line' as const,
              x0: 0,
              x1: 1,
              xref: 'paper' as const,
              y0: target,
              y1: target,
              line: { dash: 'dash' as const, color: RED, width: 1 },
            },
          ]
        : []),
    ]

    return {
      data: [
        {
          x: pd.cumulative_nfe,
          y: pd[key],
          type: 'scatter',
          mode: 'lines',
          name: label,
          line: { color, width: 2 },
          showlegend: false,
        },
      ],
      layout: {
        title: { text: label },
        xaxis: { title: { text: 'NFE' } },
        shapes,
        height: 220,
        margin: { t: 40, b: 40, l: 48, r: 16 },
      },
    }
  })
}

export function buildGainsCharts(pd: MuloPlotData): { data: Data[]; layout: Partial<Layout> }[] {
  const gains = ['Kp', 'Ki', 'Kd'] as const
  const colors = [BLUE, ORANGE, PURPLE]
  const extents = attemptNfeExtents(pd)

  return gains.map((gain, index) => {
    const shapes: NonNullable<Layout['shapes']> = []
    Object.entries(extents).forEach(([attStr, ext]) => {
      const att = Number(attStr)
      const range = pd.attempt_ranges[att]?.[gain]
      if (range) {
        const [lo, hi] = range
        shapes.push({
          type: 'rect',
          x0: ext.nfe_min,
          x1: ext.nfe_max,
          y0: lo,
          y1: hi,
          fillcolor: RANGE_FILL,
          line: { width: 0 },
        })
      }
    })
    pd.attempt_boundaries_nfe.forEach((nfe) => {
      shapes.push({
        type: 'line',
        x0: nfe,
        x1: nfe,
        y0: 0,
        y1: 1,
        yref: 'paper',
        line: { dash: 'dash', color: GRAY, width: 1 },
      })
    })

    return {
      data: [
        {
          x: pd.cumulative_nfe,
          y: pd[gain],
          type: 'scatter',
          mode: 'lines',
          name: gain,
          line: { color: colors[index], width: 2 },
        },
      ],
      layout: {
        title: { text: gain },
        xaxis: { title: { text: 'NFE' } },
        shapes,
        height: 260,
        margin: { t: 40, b: 40, l: 48, r: 16 },
      },
    }
  })
}

export function buildSummaryCharts(pd: MuloPlotData): { data: Data[]; layout: Partial<Layout> }[] {
  const summaries = pd.attempt_summaries
  if (!summaries.length) return []

  const attempts = summaries.map((s) => s.attempt as number)
  const charts: { data: Data[]; layout: Partial<Layout> }[] = []

  charts.push({
    data: [
      {
        x: attempts,
        y: summaries.map((s) => s.pop_size as number),
        type: 'bar',
        name: 'Pop Size',
        marker: { color: BLUE },
      },
      {
        x: attempts,
        y: summaries.map((s) => s.num_gen as number),
        type: 'bar',
        name: 'Num Gens',
        marker: { color: ORANGE },
      },
    ],
    layout: { title: { text: 'GA Config (Pop / Gens)' }, barmode: 'group', height: 260 },
  })

  charts.push({
    data: [
      {
        x: attempts,
        y: summaries.map((s) => (s.weights as Record<string, number>)?.mse ?? 0),
        type: 'bar',
        name: 'W-MSE',
        marker: { color: BLUE },
      },
      {
        x: attempts,
        y: summaries.map((s) => (s.weights as Record<string, number>)?.settling_time ?? 0),
        type: 'bar',
        name: 'W-ST',
        marker: { color: ORANGE },
      },
    ],
    layout: { title: { text: 'Weights: MSE & Settling Time' }, barmode: 'group', height: 260 },
  })

  charts.push({
    data: [
      {
        x: attempts,
        y: summaries.map((s) => (s.success_score as number) ?? 0),
        type: 'bar',
        name: 'Score',
        marker: {
          color: summaries.map((s) => {
            const score = (s.success_score as number) ?? 0
            if (score === 100) return GREEN
            if (score >= 50) return ORANGE
            return RED
          }),
        },
      },
    ],
    layout: { title: { text: 'Success Score' }, height: 260, yaxis: { range: [0, 110] } },
  })

  return charts
}

export function buildPerformanceChart(
  time: number[],
  actual: number[],
  reference: number[],
  signalType: string,
  yLabel: string,
  unit: string,
): { data: Data[]; layout: Partial<Layout> } {
  return {
    data: [
      {
        x: time,
        y: actual,
        type: 'scatter',
        mode: 'lines',
        name: `${signalType} Actual Value`,
        line: { color: BLUE, width: 2 },
      },
      {
        x: time,
        y: reference,
        type: 'scatter',
        mode: 'lines',
        name: `${signalType} Reference Setpoint`,
        line: { dash: 'dash', color: RED, width: 2 },
      },
    ],
    layout: {
      title: { text: `System Temporal Tracking Response: ${signalType} Input` },
      xaxis: { title: { text: 'Time (seconds)' } },
      yaxis: { title: { text: `${yLabel} (${unit})` } },
      height: 380,
    },
  }
}

export function latestPlotMetrics(pd: MuloPlotData | null) {
  if (!pd?.cumulative_nfe.length) {
    return { attempt: null, nfe: null, bestCost: null, successScore: null }
  }
  const last = pd.cumulative_nfe.length - 1
  return {
    attempt: pd.attempt[last] ?? null,
    nfe: pd.cumulative_nfe[last] ?? null,
    bestCost: pd.best_baseline_so_far[last] ?? null,
    successScore: pd.success_score[last] ?? null,
  }
}
