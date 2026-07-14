import { useEffect, useState } from 'react'
import type { MuloLoopMetrics, MuloPidLoop } from '../lib/muloDesignConfig'
import { btnBase, btnPrimary, cardPanel, fieldInput, fieldLabel } from '../lib/classes'

interface MuloCaseStudyEditorProps {
  controllerStructure: MuloPidLoop[]
  simulationParams: { dt: number; max_time: number }
  loopIndex: number
  onBack: () => void
  onReset: () => void
  onRun: (structure: MuloPidLoop[], simulationParams: { dt: number; max_time: number }) => void
  loading?: boolean
}

function defaultMetrics(): MuloLoopMetrics {
  return { mse: 0.001, settling_time: 7, overshoot: 15, control_effort: 0.25 }
}

export function MuloCaseStudyEditor({
  controllerStructure,
  simulationParams,
  loopIndex,
  onBack,
  onReset,
  onRun,
  loading = false,
}: MuloCaseStudyEditorProps) {
  const [structure, setStructure] = useState(controllerStructure)
  const [simParams, setSimParams] = useState(simulationParams)

  useEffect(() => {
    setStructure(controllerStructure)
    setSimParams(simulationParams)
  }, [controllerStructure, simulationParams])

  const updateMetric = (loopIdx: number, key: keyof MuloLoopMetrics, value: number) => {
    setStructure((prev) =>
      prev.map((loop, index) =>
        index === loopIdx
          ? {
              ...loop,
              metrics: { ...(loop.metrics ?? defaultMetrics()), [key]: value },
            }
          : loop,
      ),
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <button type="button" className={btnBase} onClick={onBack}>
          Back to Parameter Configurations
        </button>
        <button type="button" className={btnBase} onClick={onReset}>
          Reset to Default Values
        </button>
      </div>

      <div className={cardPanel}>
        <h3 className="mt-0 mb-3 text-foreground">Simulation Parameters</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <label className={fieldLabel}>
            <span>Time Step Size Delta (dt)</span>
            <input
              type="number"
              className={fieldInput}
              min={0.0001}
              max={0.1}
              step={0.0005}
              value={simParams.dt}
              onChange={(e) => setSimParams((prev) => ({ ...prev, dt: Number(e.target.value) }))}
            />
          </label>
          <label className={fieldLabel}>
            <span>Maximum Processing Epoch Run Time (s)</span>
            <input
              type="number"
              className={fieldInput}
              min={1}
              max={300}
              step={1}
              value={simParams.max_time}
              onChange={(e) =>
                setSimParams((prev) => ({ ...prev, max_time: Number(e.target.value) }))
              }
            />
          </label>
        </div>
      </div>

      <div className={cardPanel}>
        <h3 className="mt-0 mb-3 text-foreground">Fixed Performance Targets</h3>
        {structure.map((loop, index) => (
          <div key={loop.loop_number} className="mb-5 last:mb-0">
            <h4 className="text-sm font-semibold text-foreground mb-3 capitalize">
              Loop Context: {loop.loop_name.replace(/_/g, ' ')}
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <label className={fieldLabel}>
                <span>Mean Squared Error (mse)</span>
                <input
                  type="number"
                  className={fieldInput}
                  min={0}
                  step={0.001}
                  value={loop.metrics?.mse ?? 0.001}
                  onChange={(e) => updateMetric(index, 'mse', Number(e.target.value))}
                />
              </label>
              <label className={fieldLabel}>
                <span>Settling Time Threshold (s)</span>
                <input
                  type="number"
                  className={fieldInput}
                  min={0}
                  step={0.5}
                  value={loop.metrics?.settling_time ?? 7}
                  onChange={(e) => updateMetric(index, 'settling_time', Number(e.target.value))}
                />
              </label>
              <label className={fieldLabel}>
                <span>Maximum Percentage Overshoot (%)</span>
                <input
                  type="number"
                  className={fieldInput}
                  min={0}
                  max={100}
                  step={0.5}
                  value={loop.metrics?.overshoot ?? 15}
                  onChange={(e) => updateMetric(index, 'overshoot', Number(e.target.value))}
                />
              </label>
              <label className={fieldLabel}>
                <span>Control Effort Penalty Weight</span>
                <input
                  type="number"
                  className={fieldInput}
                  min={0}
                  step={0.1}
                  value={loop.metrics?.control_effort ?? 0.25}
                  onChange={(e) => updateMetric(index, 'control_effort', Number(e.target.value))}
                />
              </label>
            </div>
          </div>
        ))}
      </div>

      <button
        type="button"
        className={btnPrimary}
        disabled={loading}
        onClick={() => onRun(structure, simParams)}
      >
        Run Controller Design Optimization (Loop {loopIndex + 1})
      </button>
    </div>
  )
}
