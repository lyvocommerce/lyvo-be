'use client'

import { useEffect, useState } from 'react'
import WebApp from '@twa-dev/sdk'
import { TelegramUser } from '@/types/telegram'

export default function Home() {
  const [user, setUser] = useState<TelegramUser | null>(null)
  const [isReady, setIsReady] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Initialize Telegram Web App
    WebApp.ready()
    WebApp.expand()

    // Get user data from Telegram Web App
    const initData = WebApp.initData
    const userData = WebApp.initDataUnsafe?.user

    if (userData) {
      setUser({
        id: userData.id,
        firstName: userData.first_name,
        lastName: userData.last_name || '',
        username: userData.username || '',
        languageCode: userData.language_code || '',
        isPremium: userData.is_premium || false,
        photoUrl: userData.photo_url || '',
      })
      setIsReady(true)
    } else if (initData) {
      // If we have initData but no user, try to validate via API
      fetch('/api/auth/telegram', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ initData }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success && data.user) {
            setUser({
              id: data.user.id,
              firstName: data.user.first_name,
              lastName: data.user.last_name || '',
              username: data.user.username || '',
              languageCode: data.user.language_code || '',
              isPremium: data.user.is_premium || false,
              photoUrl: data.user.photo_url || '',
            })
            setIsReady(true)
          } else {
            setError(data.error || 'Authentication failed')
          }
        })
        .catch((err) => {
          console.error('Auth error:', err)
          setError('Authentication validation failed')
        })
    } else {
      setError('No initialization data found')
    }

    // Set up Telegram theme colors
    if (WebApp.themeParams) {
      document.documentElement.style.setProperty(
        '--tg-theme-bg-color',
        WebApp.themeParams.bg_color || '#ffffff'
      )
      document.documentElement.style.setProperty(
        '--tg-theme-text-color',
        WebApp.themeParams.text_color || '#000000'
      )
      document.documentElement.style.setProperty(
        '--tg-theme-hint-color',
        WebApp.themeParams.hint_color || '#999999'
      )
      document.documentElement.style.setProperty(
        '--tg-theme-link-color',
        WebApp.themeParams.link_color || '#2481cc'
      )
      document.documentElement.style.setProperty(
        '--tg-theme-button-color',
        WebApp.themeParams.button_color || '#2481cc'
      )
      document.documentElement.style.setProperty(
        '--tg-theme-button-text-color',
        WebApp.themeParams.button_text_color || '#ffffff'
      )
      document.documentElement.style.setProperty(
        '--tg-theme-secondary-bg-color',
        WebApp.themeParams.secondary_bg_color || '#f1f1f1'
      )
    }

    // Handle back button
    WebApp.BackButton.onClick(() => {
      WebApp.BackButton.hide()
      // Handle navigation or close
    })

    return () => {
      WebApp.BackButton.offClick(() => {})
    }
  }, [])

  const handleButtonClick = () => {
    WebApp.showAlert('Button clicked!')
  }

  const handleMainButtonClick = () => {
    WebApp.showConfirm('Are you sure?', (confirmed: boolean) => {
      if (confirmed) {
        WebApp.showAlert('Confirmed!')
      }
    })
  }

  if (!isReady) {
    return (
      <main style={{ padding: '20px', textAlign: 'center' }}>
        {!error && <p>Loading...</p>}
        {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
      </main>
    )
  }

  if (isReady && !user) {
    return (
      <main style={{ padding: '20px', textAlign: 'center' }}>
        <p>No user data found</p>
      </main>
    )
  }

  return (
    <main style={{ padding: '20px', minHeight: '100vh' }}>
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ marginBottom: '20px', fontSize: '24px', fontWeight: 'bold' }}>
          Welcome to LyvoShop!
        </h1>
        
        {user && (
          <div style={{
            background: 'var(--tg-theme-secondary-bg-color)',
            padding: '15px',
            borderRadius: '10px',
            marginBottom: '20px'
          }}>
            <h2 style={{ marginBottom: '10px', fontSize: '18px' }}>User Info</h2>
            <p><strong>Name:</strong> {user.firstName} {user.lastName}</p>
            {user.username && <p><strong>Username:</strong> @{user.username}</p>}
            <p><strong>ID:</strong> {user.id}</p>
            {user.isPremium && <p><strong>Premium:</strong> ✓</p>}
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button
            onClick={handleButtonClick}
            style={{
              padding: '12px 24px',
              backgroundColor: 'var(--tg-theme-button-color)',
              color: 'var(--tg-theme-button-text-color)',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            Show Alert
          </button>

          <button
            onClick={handleMainButtonClick}
            style={{
              padding: '12px 24px',
              backgroundColor: 'var(--tg-theme-secondary-bg-color)',
              color: 'var(--tg-theme-text-color)',
              border: '1px solid var(--tg-theme-hint-color)',
              borderRadius: '8px',
              fontSize: '16px',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            Show Confirm
          </button>
        </div>

        <div style={{ marginTop: '30px', padding: '15px', background: 'var(--tg-theme-secondary-bg-color)', borderRadius: '10px' }}>
          <h3 style={{ marginBottom: '10px' }}>Telegram Web App Info</h3>
          <p style={{ fontSize: '14px', color: 'var(--tg-theme-hint-color)' }}>
            Platform: {WebApp.platform}
          </p>
          <p style={{ fontSize: '14px', color: 'var(--tg-theme-hint-color)' }}>
            Version: {WebApp.version}
          </p>
        </div>
      </div>
    </main>
  )
}

