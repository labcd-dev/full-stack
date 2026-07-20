import { useCallback, useState } from 'react'
import { surveyApi } from '../api/endpoints'
import { FeedbackSurveyModal } from '../components/FeedbackSurveyModal'
import { useAuth } from '../context/AuthContext'

/**
 * After a successful SILO/MULO design run, prompt for feedback if the survey
 * module is enabled and the user has not submitted yet.
 */
export function useFeedbackSurveyPrompt() {
  const { user, refreshUser } = useAuth()
  const [open, setOpen] = useState(false)

  const promptAfterDesignSuccess = useCallback(async () => {
    if (!user) return
    if (user.feedback_survey_completed) return
    try {
      const status = await surveyApi.status()
      if (!status.enabled || status.feedback_completed) return
      setOpen(true)
    } catch {
      // Ignore status failures; do not block the design UX.
    }
  }, [user])

  const modal = (
    <FeedbackSurveyModal
      open={open}
      onDismiss={() => setOpen(false)}
      onSubmitted={async () => {
        setOpen(false)
        await refreshUser()
      }}
    />
  )

  return { promptAfterDesignSuccess, feedbackModal: modal }
}
