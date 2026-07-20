import { useState } from 'react'
import { ChevronLeft, ChevronRight, X } from 'lucide-react'
import { surveyApi } from '../api/endpoints'
import type { TutorialVideo } from '../api/types'
import { StatusMessage } from './StatusMessage'
import { btnBase, btnPrimary } from '../lib/classes'

const REMIND_LATER_KEY = 'labcd_tutorial_remind_later'

export function isTutorialRemindLater(): boolean {
  return sessionStorage.getItem(REMIND_LATER_KEY) === '1'
}

export function setTutorialRemindLater(): void {
  sessionStorage.setItem(REMIND_LATER_KEY, '1')
}

interface TutorialSliderModalProps {
  videos: TutorialVideo[]
  onClosed: () => void | Promise<void>
  /** Onboarding shows dismiss actions; browse mode is a simple viewer. */
  mode?: 'onboarding' | 'browse'
}

export function TutorialSliderModal({
  videos,
  onClosed,
  mode = 'onboarding',
}: TutorialSliderModalProps) {
  const [index, setIndex] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  if (videos.length === 0) return null

  const current = videos[index]
  const canPrev = index > 0
  const canNext = index < videos.length - 1

  const handleRemindLater = async () => {
    setTutorialRemindLater()
    try {
      await surveyApi.dismissTutorial('remind_later')
    } catch {
      // Session skip still applies even if API call fails.
    }
    await onClosed()
  }

  const handleDontShowAgain = async () => {
    setSaving(true)
    setError(null)
    try {
      await surveyApi.dismissTutorial('dont_show_again')
      await onClosed()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save preference')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div
        className="admin-fade-in absolute inset-0 bg-foreground/45 backdrop-blur-[2px]"
        onClick={() => {
          if (mode === 'browse') void onClosed()
        }}
      />
      <div
        className="admin-slide-in relative z-10 flex w-full max-w-3xl max-h-[92vh] flex-col overflow-hidden rounded-2xl border border-border bg-surface-elevated shadow-2xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="tutorial-slider-title"
      >
        <div className="flex items-start justify-between gap-3 border-b border-border px-5 py-4">
          <div className="min-w-0">
            <h2 id="tutorial-slider-title" className="m-0 text-lg font-semibold text-foreground">
              {current.title}
            </h2>
            <p className="mt-1 text-sm text-muted-text">
              How LabCD works · {index + 1} / {videos.length}
            </p>
          </div>
          {mode === 'browse' && (
            <button
              type="button"
              className={btnBase}
              onClick={() => void onClosed()}
              aria-label="Close tutorials"
            >
              <X className="size-4" />
            </button>
          )}
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4">
          <video
            key={current.id}
            className="aspect-video w-full rounded-xl bg-black object-contain"
            src={current.file_url}
            controls
            playsInline
          />
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border px-5 py-4">
          <div className="flex items-center gap-2">
            <button
              type="button"
              className={btnBase}
              disabled={!canPrev}
              onClick={() => setIndex((i) => Math.max(0, i - 1))}
              aria-label="Previous video"
            >
              <ChevronLeft className="size-4" />
              Prev
            </button>
            <button
              type="button"
              className={btnBase}
              disabled={!canNext}
              onClick={() => setIndex((i) => Math.min(videos.length - 1, i + 1))}
              aria-label="Next video"
            >
              Next
              <ChevronRight className="size-4" />
            </button>
          </div>

          {mode === 'onboarding' ? (
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                className={btnBase}
                disabled={saving}
                onClick={() => void handleRemindLater()}
              >
                Remind me later
              </button>
              <button
                type="button"
                className={btnPrimary}
                disabled={saving}
                onClick={() => void handleDontShowAgain()}
              >
                {saving ? 'Saving…' : "Don't show again"}
              </button>
            </div>
          ) : (
            <button type="button" className={btnPrimary} onClick={() => void onClosed()}>
              Close
            </button>
          )}
        </div>

        {error && (
          <div className="px-5 pb-4">
            <StatusMessage type="error" message={error} />
          </div>
        )}
      </div>
    </div>
  )
}
