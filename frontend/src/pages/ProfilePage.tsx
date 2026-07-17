import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { Camera, Trash2, User } from 'lucide-react'
import { authApi } from '../api/endpoints'
import { StatusMessage } from '../components/StatusMessage'
import { useAuth } from '../context/AuthContext'
import { useTheme, type ThemeMode } from '../context/ThemeContext'
import {
  btnBase,
  btnPrimary,
  cardPanel,
  fieldInput,
  fieldLabel,
  pageIntro,
  pageSection,
  pageTitle,
} from '../lib/classes'

const THEME_OPTIONS: { value: ThemeMode; label: string; description: string }[] = [
  { value: 'light', label: 'Light', description: 'Always use the light theme' },
  { value: 'dark', label: 'Dark', description: 'Always use the dark theme' },
  { value: 'system', label: 'System', description: 'Match your device preference' },
]

function userInitials(user: { display_name: string | null; email: string }): string {
  const source = user.display_name?.trim() || user.email
  const parts = source.split(/\s+/).filter(Boolean)
  if (parts.length >= 2) {
    return `${parts[0][0] ?? ''}${parts[1][0] ?? ''}`.toUpperCase()
  }
  return source.slice(0, 2).toUpperCase()
}

export function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const { theme, setTheme } = useTheme()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [emailPassword, setEmailPassword] = useState('')
  const [selectedTheme, setSelectedTheme] = useState<ThemeMode>('system')

  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const [profileMessage, setProfileMessage] = useState<string | null>(null)
  const [profileError, setProfileError] = useState<string | null>(null)
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null)
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [avatarError, setAvatarError] = useState<string | null>(null)

  const [savingProfile, setSavingProfile] = useState(false)
  const [savingPassword, setSavingPassword] = useState(false)
  const [uploadingAvatar, setUploadingAvatar] = useState(false)

  useEffect(() => {
    if (!user) return
    setDisplayName(user.display_name ?? '')
    setEmail(user.email)
    setSelectedTheme(user.theme)
  }, [user])

  if (!user) {
    return null
  }

  const emailChanged = email.trim().toLowerCase() !== user.email.toLowerCase()
  const profileChanged =
    (displayName.trim() || null) !== (user.display_name ?? null) ||
    selectedTheme !== user.theme ||
    emailChanged

  const handleProfileSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setProfileMessage(null)
    setProfileError(null)

    if (emailChanged && !emailPassword) {
      setProfileError('Enter your current password to change email')
      return
    }

    setSavingProfile(true)
    try {
      const body: {
        display_name: string | null
        email?: string
        theme: ThemeMode
        current_password?: string
      } = {
        display_name: displayName.trim() || null,
        theme: selectedTheme,
      }
      if (emailChanged) {
        body.email = email.trim()
        body.current_password = emailPassword
      }

      await authApi.updateProfile(body)
      await refreshUser()
      setTheme(selectedTheme)
      setEmailPassword('')
      setProfileMessage('Profile updated')
    } catch (err) {
      setProfileError(err instanceof Error ? err.message : 'Failed to update profile')
    } finally {
      setSavingProfile(false)
    }
  }

  const handlePasswordSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setPasswordMessage(null)
    setPasswordError(null)

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match')
      return
    }
    if (newPassword.length < 6) {
      setPasswordError('New password must be at least 6 characters')
      return
    }

    setSavingPassword(true)
    try {
      await authApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      })
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setPasswordMessage('Password changed')
    } catch (err) {
      setPasswordError(err instanceof Error ? err.message : 'Failed to change password')
    } finally {
      setSavingPassword(false)
    }
  }

  const handleAvatarSelect = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return

    setAvatarError(null)
    setUploadingAvatar(true)
    try {
      await authApi.uploadAvatar(file)
      await refreshUser()
    } catch (err) {
      setAvatarError(err instanceof Error ? err.message : 'Failed to upload avatar')
    } finally {
      setUploadingAvatar(false)
    }
  }

  const handleRemoveAvatar = async () => {
    setAvatarError(null)
    setUploadingAvatar(true)
    try {
      await authApi.removeAvatar()
      await refreshUser()
    } catch (err) {
      setAvatarError(err instanceof Error ? err.message : 'Failed to remove avatar')
    } finally {
      setUploadingAvatar(false)
    }
  }

  return (
    <section className={pageSection}>
      <header>
        <h1 className={pageTitle}>Profile</h1>
        <p className={pageIntro}>
          Manage your account details, profile picture, password, and default appearance.
        </p>
      </header>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
        <div className={`${cardPanel} space-y-4`}>
          <h2 className="m-0 text-lg font-semibold text-foreground">Profile picture</h2>
          <div className="flex items-center gap-4">
            <div className="relative flex size-24 shrink-0 items-center justify-center overflow-hidden rounded-full border border-border bg-surface-muted text-xl font-semibold text-primary">
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt=""
                  className="size-full object-cover"
                />
              ) : (
                <span aria-hidden>{userInitials(user)}</span>
              )}
            </div>
            <div className="space-y-2">
              <p className="m-0 text-sm text-muted-text">
                Upload a JPEG, PNG, WebP, or GIF up to 2 MB.
              </p>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className={btnPrimary}
                  disabled={uploadingAvatar}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Camera className="size-4" aria-hidden />
                  {uploadingAvatar ? 'Uploading…' : 'Upload photo'}
                </button>
                {user.avatar_url && (
                  <button
                    type="button"
                    className={btnBase}
                    disabled={uploadingAvatar}
                    onClick={() => void handleRemoveAvatar()}
                  >
                    <Trash2 className="size-4" aria-hidden />
                    Remove
                  </button>
                )}
              </div>
            </div>
          </div>
          {avatarError && <StatusMessage type="error" message={avatarError} />}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            className="hidden"
            onChange={(e) => void handleAvatarSelect(e)}
          />
        </div>

        <div className={`${cardPanel} space-y-4`}>
          <h2 className="m-0 text-lg font-semibold text-foreground">Account</h2>
          {profileMessage && <StatusMessage type="success" message={profileMessage} />}
          {profileError && <StatusMessage type="error" message={profileError} />}

          <form onSubmit={(e) => void handleProfileSubmit(e)} className="space-y-1">
            <label className={fieldLabel}>
              <span>Display name</span>
              <input
                className={fieldInput}
                type="text"
                maxLength={100}
                placeholder="Optional"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
              />
            </label>
            <label className={fieldLabel}>
              <span>Email</span>
              <input
                className={fieldInput}
                type="email"
                autoComplete="username"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>
            {emailChanged && (
              <label className={fieldLabel}>
                <span>Current password</span>
                <input
                  className={fieldInput}
                  type="password"
                  autoComplete="current-password"
                  required
                  value={emailPassword}
                  onChange={(e) => setEmailPassword(e.target.value)}
                />
              </label>
            )}
            <fieldset className="mb-4 border-none p-0">
              <legend className="mb-3 text-sm font-medium text-foreground">Default theme</legend>
              <div className="grid gap-2 sm:grid-cols-3">
                {THEME_OPTIONS.map((option) => (
                  <label
                    key={option.value}
                    className={`cursor-pointer rounded-lg border px-3 py-3 transition-colors ${
                      selectedTheme === option.value
                        ? 'border-primary bg-[color-mix(in_srgb,var(--app-primary)_10%,transparent)]'
                        : 'border-border-input bg-surface-elevated hover:border-primary/50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="theme"
                      value={option.value}
                      checked={selectedTheme === option.value}
                      onChange={() => setSelectedTheme(option.value)}
                      className="sr-only"
                    />
                    <span className="block text-sm font-medium text-foreground">{option.label}</span>
                    <span className="mt-1 block text-xs text-muted-text">{option.description}</span>
                  </label>
                ))}
              </div>
              <p className="mt-2 text-xs text-muted-text">
                Current appearance: {theme === 'system' ? 'System' : theme}
              </p>
            </fieldset>
            <button
              type="submit"
              className={btnPrimary}
              disabled={savingProfile || !profileChanged}
            >
              {savingProfile ? 'Saving…' : 'Save profile'}
            </button>
          </form>
        </div>
      </div>

      <div className={`${cardPanel} max-w-xl space-y-4`}>
        <h2 className="m-0 text-lg font-semibold text-foreground">Change password</h2>
        {passwordMessage && <StatusMessage type="success" message={passwordMessage} />}
        {passwordError && <StatusMessage type="error" message={passwordError} />}

        <form onSubmit={(e) => void handlePasswordSubmit(e)} className="space-y-1">
          <label className={fieldLabel}>
            <span>Current password</span>
            <input
              className={fieldInput}
              type="password"
              autoComplete="current-password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
            />
          </label>
          <label className={fieldLabel}>
            <span>New password</span>
            <input
              className={fieldInput}
              type="password"
              autoComplete="new-password"
              required
              minLength={6}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
          </label>
          <label className={fieldLabel}>
            <span>Confirm new password</span>
            <input
              className={fieldInput}
              type="password"
              autoComplete="new-password"
              required
              minLength={6}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </label>
          <button type="submit" className={btnPrimary} disabled={savingPassword}>
            {savingPassword ? 'Updating…' : 'Update password'}
          </button>
        </form>
      </div>

      <div className={`${cardPanel} text-sm text-muted-text`}>
        <div className="flex items-center gap-2 text-foreground">
          <User className="size-4" aria-hidden />
          <span className="font-medium">Account info</span>
        </div>
        <p className="mb-1 mt-3">
          Role: {user.is_admin ? 'Administrator' : 'User'}
        </p>
        <p className="m-0">Member since {new Date(user.created_at).toLocaleDateString()}</p>
      </div>
    </section>
  )
}
