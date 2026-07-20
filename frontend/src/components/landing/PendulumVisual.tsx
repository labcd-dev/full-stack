type PendulumVisualProps = {
  caption: string
}

export function PendulumVisual({ caption }: PendulumVisualProps) {
  return (
    <div className="relative mt-16 w-full max-w-4xl">
      <div
        className="absolute -bottom-6 left-1/2 h-24 w-4/5 -translate-x-1/2 rounded-full blur-3xl"
        style={{ backgroundColor: 'color-mix(in srgb, var(--brand-primary) 20%, transparent)' }}
      />
      <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-white/5 shadow-[0_0_0_1px_rgba(255,255,255,0.03),0_30px_80px_rgba(0,0,0,0.35)] backdrop-blur-sm">
        <div className="relative flex min-h-[440px] items-center justify-center overflow-hidden p-6 sm:min-h-[520px] sm:p-10">
          <div className="control-grid absolute inset-0 opacity-40 [background-image:linear-gradient(color-mix(in_srgb,var(--brand-primary)_8%,transparent)_1px,transparent_1px),linear-gradient(90deg,color-mix(in_srgb,var(--brand-primary)_8%,transparent)_1px,transparent_1px)] [background-size:160px_160px]" />
          <div
            className="pointer-events-none absolute left-1/2 top-1/2 h-[480px] w-[480px] -translate-x-1/2 -translate-y-1/2 rounded-full blur-3xl"
            style={{ backgroundColor: 'color-mix(in srgb, var(--brand-primary) 10%, transparent)' }}
          />
          <svg viewBox="0 0 800 520" className="relative z-10 h-full w-full max-w-[760px]" aria-hidden>
            <circle cx="400" cy="300" r="150" fill="none" stroke="color-mix(in srgb, var(--brand-primary) 6%, transparent)" strokeWidth="2" />
            <circle cx="400" cy="300" r="95" fill="none" stroke="color-mix(in srgb, var(--brand-primary) 8%, transparent)" strokeWidth="2" strokeDasharray="8 14" className="control-signal" />
            <line x1="160" y1="370" x2="640" y2="370" stroke="color-mix(in srgb, var(--brand-primary) 14%, transparent)" strokeWidth="3" strokeLinecap="round" />
            <line x1="180" y1="370" x2="620" y2="370" stroke="var(--brand-primary)" strokeWidth="2" strokeLinecap="round" className="control-signal base-active-glow" />
            <g className="control-cart">
              <ellipse cx="400" cy="381" rx="132" ry="18" fill="color-mix(in srgb, var(--brand-primary) 12%, transparent)" />
              <rect x="320" y="300" width="160" height="58" rx="14" fill="rgba(15,23,42,0.78)" stroke="var(--brand-primary)" strokeWidth="3" />
              <rect x="330" y="310" width="140" height="18" rx="8" fill="color-mix(in srgb, var(--brand-primary) 8%, transparent)" />
              <g className="control-pendulum">
                <line x1="400" y1="300" x2="400" y2="145" stroke="var(--brand-primary)" strokeWidth="5" strokeLinecap="round" />
                <circle cx="400" cy="145" r="16" fill="var(--brand-primary)" />
              </g>
              <g className="control-wheel-left">
                <circle cx="348" cy="358" r="15" fill="rgba(15,23,42,0.95)" stroke="var(--brand-primary)" strokeWidth="3" />
              </g>
              <g className="control-wheel-right">
                <circle cx="452" cy="358" r="15" fill="rgba(15,23,42,0.95)" stroke="var(--brand-primary)" strokeWidth="3" />
              </g>
            </g>
          </svg>
          <div className="absolute bottom-5 left-1/2 -translate-x-1/2 text-center text-sm font-medium tracking-wide text-white/40 sm:text-base">
            {caption}
          </div>
        </div>
      </div>
    </div>
  )
}
