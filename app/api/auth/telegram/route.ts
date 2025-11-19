import { NextRequest, NextResponse } from 'next/server'
import { validateTelegramWebAppData, parseInitData } from '@/lib/telegram-auth'

/**
 * API route to validate Telegram authentication
 * This can be used for server-side validation
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { initData } = body

    if (!initData) {
      return NextResponse.json(
        { error: 'No initData provided' },
        { status: 400 }
      )
    }

    // Validate the initData
    const isValid = validateTelegramWebAppData(initData)

    if (!isValid) {
      return NextResponse.json(
        { error: 'Invalid authentication data' },
        { status: 401 }
      )
    }

    // Parse user data
    const userData = parseInitData(initData)

    return NextResponse.json({
      success: true,
      user: userData,
    })
  } catch (error) {
    console.error('Auth error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

