import { useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

/** Apply the signed-in user's saved theme preference after login or profile refresh. */
export function UserThemeSync() {
  const { user } = useAuth()
  const { setTheme } = useTheme()

  useEffect(() => {
    if (user?.theme) {
      setTheme(user.theme)
    }
  }, [user?.theme, setTheme])

  return null
}
