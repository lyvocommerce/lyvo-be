# LyvoShop Telegram Web App

A Next.js application designed to work within Telegram as a Web App with integrated authentication.

## Features

- ✅ Telegram Web App SDK integration
- ✅ Telegram authentication with initData validation
- ✅ Automatic theme adaptation (light/dark mode)
- ✅ TypeScript support
- ✅ Responsive UI optimized for Telegram

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.local.example .env.local
   ```
   
   Then edit `.env.local` and add your Telegram Bot token:
   - `TELEGRAM_BOT_TOKEN` or `TELEGRAM_BOT_SECRET`: Your bot token from @BotFather (used for validating initData)
   
   **Note:** The bot token is used as the secret for validating Telegram Web App initData. Never expose it in client-side code!

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   npm start
   ```

## Telegram Bot Setup

1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Get your bot token
3. Set up a Web App:
   - Use `/newapp` command in BotFather
   - Provide a title and description
   - Set the Web App URL to your deployed Next.js app URL
   - For local development, you can use a service like [ngrok](https://ngrok.com/) to expose your local server

## Authentication & Validation

Telegram Web App validation uses your bot token as the secret. The validation process:

1. Telegram sends `initData` with user information and a hash
2. Server validates the hash using: `HMAC-SHA256(secret_key, data_check_string)`
3. Where `secret_key = HMAC-SHA256("WebAppData", bot_token)`

**Important:** 
- Always validate `initData` on the server side in production
- Never expose your bot token in client-side code
- The validation happens automatically via the `/api/auth/telegram` endpoint
- For development, the app will work without validation, but it's recommended to set up the bot token

## Project Structure

```
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── telegram/
│   │           └── route.ts    # API route for server-side auth validation
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Main page component
│   └── globals.css              # Global styles with Telegram theme support
├── lib/
│   └── telegram-auth.ts         # Authentication utilities
├── types/
│   └── telegram.ts              # TypeScript types for Telegram
└── package.json
```

## Usage

The app automatically:
- Initializes the Telegram Web App SDK
- Validates user authentication
- Adapts to Telegram's theme (light/dark mode)
- Provides access to Telegram Web App features (alerts, confirms, etc.)

## Development

The app uses:
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **@twa-dev/sdk** for Telegram Web App integration

## Security Notes

- Always validate `initData` on the server side for production
- Never expose your bot secret in client-side code
- Use environment variables for sensitive data

