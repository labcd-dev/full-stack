import Plot from 'react-plotly.js'
import type { Data, Layout } from 'plotly.js'
import { useTheme } from '../context/ThemeContext'

interface PlotlyChartProps {
  data: Data[]
  layout?: Partial<Layout>
  height?: number
  className?: string
}

export function PlotlyChart({ data, layout = {}, height = 360, className }: PlotlyChartProps) {
  const { resolvedTheme } = useTheme()
  const isDark = resolvedTheme === 'dark'

  const mergedLayout: Partial<Layout> = {
    autosize: true,
    height,
    margin: { l: 48, r: 24, t: 40, b: 40 },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: {
      color: isDark ? '#c9d1d9' : '#334155',
      family: 'inherit',
      size: 12,
    },
    legend: {
      orientation: 'h',
      y: 1.12,
      x: 0,
      bgcolor: 'transparent',
    },
    ...layout,
    xaxis: {
      gridcolor: isDark ? '#30363d' : '#e8edf5',
      zerolinecolor: isDark ? '#484f58' : '#dde3ef',
      ...(layout.xaxis ?? {}),
    },
    yaxis: {
      gridcolor: isDark ? '#30363d' : '#e8edf5',
      zerolinecolor: isDark ? '#484f58' : '#dde3ef',
      ...(layout.yaxis ?? {}),
    },
  }

  return (
    <div className={className ?? 'w-full min-h-[280px]'}>
      <Plot
        data={data}
        layout={mergedLayout}
        config={{
          displayModeBar: false,
          responsive: true,
        }}
        useResizeHandler
        style={{ width: '100%', height: `${height}px` }}
      />
    </div>
  )
}
