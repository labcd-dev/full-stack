import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Home, LogOut, Users } from 'lucide-react'
import { ThemeToggle } from './ThemeToggle'
import { useAuth } from '../context/AuthContext'
import { btnBase, btnCompact } from '../lib/classes'

export function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const isHome = location.pathname === '/'
  const isAdmin = location.pathname.startsWith('/admin')
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen flex flex-col bg-surface">
      <header className="sticky top-0 z-10 flex justify-between items-center gap-4 px-6 py-3.5 bg-surface-elevated/95 backdrop-blur-sm border-b border-border shadow-sm max-md:flex-col max-md:items-start">
        <Link to="/" className="flex items-center gap-3 group">
          <img
            src="/logo.svg"
            alt="LabCD"
            className="w-11 h-11 transition-transform duration-200 group-hover:scale-105"
          />
          <div>
            <h1 className="m-0 text-lg font-semibold tracking-tight text-foreground">
              LabCD
            </h1>
            <p className="m-0 text-muted text-xs">
              AI-Powered Control System Design Studio
            </p>
          </div>
        </Link>
        <div className="flex items-center gap-3 flex-wrap max-md:w-full max-md:justify-between">
          {user && (
            <nav className="flex gap-1">
              <Link
                to="/"
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isHome
                    ? 'bg-[color-mix(in_srgb,var(--app-primary)_12%,transparent)] text-primary'
                    : 'text-muted-text hover:text-foreground hover:bg-surface-hover'
                }`}
              >
                <Home className="size-4" aria-hidden />
                Home
              </Link>
              {user.is_admin && (
                <Link
                  to="/admin/users"
                  className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isAdmin
                      ? 'bg-[color-mix(in_srgb,var(--app-primary)_12%,transparent)] text-primary'
                      : 'text-muted-text hover:text-foreground hover:bg-surface-hover'
                  }`}
                >
                  <Users className="size-4" aria-hidden />
                  Users
                </Link>
              )}
            </nav>
          )}
          <div className="flex items-center gap-2">
            {user && (
              <>
                <span className="text-sm text-muted-text max-md:hidden">{user.email}</span>
                <button
                  type="button"
                  className={`${btnBase} ${btnCompact}`}
                  onClick={handleLogout}
                  title="Sign out"
                >
                  <LogOut className="size-3.5" aria-hidden />
                  Sign out
                </button>
              </>
            )}
            <ThemeToggle />
          </div>
        </div>
      </header>
      <main className="flex-1 p-6 max-w-[1200px] w-full mx-auto">
        <Outlet />
      </main>
      <footer className="text-center py-4 px-6 text-muted text-xs border-t border-border">
        LabCD Control Design Studio
      </footer>
    </div>
  )
}
