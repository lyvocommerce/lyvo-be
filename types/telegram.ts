export interface TelegramUser {
  id: number
  firstName: string
  lastName: string
  username: string
  languageCode: string
  isPremium: boolean
  photoUrl: string
}

export interface TelegramWebAppInitData {
  query_id?: string
  user?: {
    id: number
    first_name: string
    last_name?: string
    username?: string
    language_code?: string
    is_premium?: boolean
    photo_url?: string
  }
  auth_date: number
  hash: string
}

