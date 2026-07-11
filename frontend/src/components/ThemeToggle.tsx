import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import { btnBase, btnCompact } from '../lib/classes'

export function ThemeToggle() {
  const { resolvedTheme, toggleTheme } = useTheme()
  const isDark = resolvedTheme === 'dark'

  return (
    <button
      type="button"
      className={`${btnBase} ${btnCompact}`}
      onClick={toggleTheme}
      aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
      title={isDark ? 'Light mode' : 'Dark mode'}
    >
      {isDark ? (
        <>
          <Sun className="size-4" aria-hidden />
          Light
        </>
      ) : (
        <>
          <Moon className="size-4" aria-hidden />
          Dark
        </>
      )}
    </button>
  )
}
