# Sofie - Tanzanian Aviation Regulations Assistant

Sofie is an AI-powered assistant that provides accurate information about Tanzanian aviation regulations. It integrates with Google Drive to maintain an up-to-date knowledge base and responds to user queries through a Telegram bot interface.

## Features

- 📚 Access to latest Tanzanian aviation regulations
- 🤖 Natural language processing for understanding queries
- 🔄 Automatic knowledge base updates
- ✅ Self-verification of answers
- 💬 User-friendly Telegram interface

## Prerequisites

- Python 3.8+
- Google Cloud Project with Drive API enabled
- Telegram Bot Token (from BotFather)
- OpenAI API Key
- Vercel account (for deployment)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sofie.git
cd sofie
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the required values:
     - `GOOGLE_DRIVE_CREDENTIALS_PATH`: Path to your Google Drive API credentials
     - `REGULATIONS_FOLDER_ID`: ID of the Google Drive folder containing regulations
     - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `VERCEL_URL`: Your Vercel deployment URL

4. Set up Google Drive API:
   - Create a project in Google Cloud Console
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials
   - Download the credentials and save as `credentials.json`

5. Set up Telegram Bot:
   - Create a new bot using BotFather
   - Get the bot token
   - Set the webhook URL to your Vercel deployment URL

## Local Development

1. Run the FastAPI server:
```bash
python -m src.api
```

2. For local testing, use ngrok to create a tunnel:
```bash
ngrok http 8000
```

3. Update the Telegram webhook URL with the ngrok URL:
```bash
curl -F "url=https://your-ngrok-url/api/webhook" https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
```

## Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy to Vercel:
```bash
vercel
```

3. Set up environment variables in Vercel dashboard

4. Update the Telegram webhook URL to your Vercel deployment URL

## Usage

1. Start a chat with your Telegram bot
2. Use `/start` to get started
3. Ask questions about Tanzanian aviation regulations
4. Use `/help` to see available commands
5. Use `/update` to force update the knowledge base

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 