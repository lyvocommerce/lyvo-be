import crypto from 'crypto'

/**
 * Validates Telegram Web App initData
 * @param initData - The initData string from Telegram Web App
 * @returns boolean indicating if the data is valid
 */
export function validateTelegramWebAppData(initData: string): boolean {
  if (!initData) {
    return false
  }

  // Get bot token from environment (used as secret for validation)
  // Note: For Telegram Web App validation, we use the bot token as the secret
  const botToken = process.env.TELEGRAM_BOT_SECRET || 
                   process.env.NEXT_PUBLIC_TELEGRAM_BOT_TOKEN ||
                   process.env.TELEGRAM_BOT_TOKEN
  
  if (!botToken) {
    console.warn('TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_SECRET not set, skipping validation')
    return true // In development, you might want to skip validation
  }

  try {
    // Parse initData
    const urlParams = new URLSearchParams(initData)
    const hash = urlParams.get('hash')
    
    if (!hash) {
      return false
    }

    // Remove hash from params for validation
    urlParams.delete('hash')

    // Sort parameters alphabetically
    const dataCheckString = Array.from(urlParams.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, value]) => `${key}=${value}`)
      .join('\n')

    // Create secret key using bot token
    // According to Telegram docs: secret_key = HMAC-SHA256("WebAppData", bot_token)
    const secretKey = crypto
      .createHmac('sha256', 'WebAppData')
      .update(botToken)
      .digest()

    // Calculate hash
    const calculatedHash = crypto
      .createHmac('sha256', secretKey)
      .update(dataCheckString)
      .digest('hex')

    // Compare hashes
    return calculatedHash === hash
  } catch (error) {
    console.error('Error validating Telegram data:', error)
    return false
  }
}

/**
 * Parses initData and returns user information
 */
export function parseInitData(initData: string) {
  const urlParams = new URLSearchParams(initData)
  const userParam = urlParams.get('user')
  
  if (!userParam) {
    return null
  }

  try {
    return JSON.parse(decodeURIComponent(userParam))
  } catch (error) {
    console.error('Error parsing user data:', error)
    return null
  }
}

