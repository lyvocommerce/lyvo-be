'use client'

import { WebApp } from '@twa-dev/sdk'

interface TelegramButtonProps {
  text: string
  onClick: () => void
  variant?: 'primary' | 'secondary'
  disabled?: boolean
}

export default function TelegramButton({
  text,
  onClick,
  variant = 'primary',
  disabled = false,
}: TelegramButtonProps) {
  const isPrimary = variant === 'primary'

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        padding: '12px 24px',
        backgroundColor: isPrimary
          ? 'var(--tg-theme-button-color)'
          : 'var(--tg-theme-secondary-bg-color)',
        color: isPrimary
          ? 'var(--tg-theme-button-text-color)'
          : 'var(--tg-theme-text-color)',
        border: isPrimary
          ? 'none'
          : '1px solid var(--tg-theme-hint-color)',
        borderRadius: '8px',
        fontSize: '16px',
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontWeight: '500',
        opacity: disabled ? 0.6 : 1,
        width: '100%',
      }}
    >
      {text}
    </button>
  )
}

