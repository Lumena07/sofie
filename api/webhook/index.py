from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json
import os
import logging
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize bot with token from environment variable
try:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
    
    application = Application.builder().token(bot_token).build()
    logger.info("Telegram bot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Telegram bot: {str(e)}")
    application = None

async def start_command(update: Update, context):
    """Handle the /start command."""
    welcome_message = (
        "👋 Welcome to Sofie, your Tanzanian Aviation Regulations Assistant!\n\n"
        "I can help you with questions about Tanzanian aviation regulations. "
        "Just ask your question, and I'll do my best to provide accurate information."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context):
    """Handle the /help command."""
    help_message = (
        "🤖 How to use Sofie:\n\n"
        "1. Simply type your question about Tanzanian aviation regulations\n"
        "2. I'll search through the latest regulations and provide an answer\n"
        "3. If I'm not confident about an answer, I'll let you know\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_message)

async def handle_message(update: Update, context):
    """Handle incoming messages."""
    try:
        query = update.message.text
        await update.message.reply_text("🔍 Processing your query...")
        
        # Make request to our query endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://{os.environ.get('VERCEL_URL')}/api/query",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                await update.message.reply_text(result["response"])
            else:
                await update.message.reply_text("❌ Sorry, I encountered an error processing your query.")
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        await update.message.reply_text("❌ Sorry, something went wrong. Please try again later.")

# Set up command handlers
if application:
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook requests from Telegram."""
    if not application:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Telegram bot not initialized"}
        )
    
    try:
        data = await request.json()
        await application.update_queue.put(Update.de_json(data=data, bot=application.bot))
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        ) 