from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import os
import logging
import requests
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI()
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def send_telegram_message(chat_id: int, text: str):
    """Send a message using Telegram API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, json=data)
    if not response.ok:
        logger.error(f"Failed to send message: {response.status_code} - {response.text}")

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook requests from Telegram."""
    try:
        data = await request.json()
        logger.info(f"Received webhook data: {json.dumps(data)[:200]}...")
        
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        if not chat_id:
            return JSONResponse(status_code=400, content={"error": "No chat_id found"})
            
        if text == "/start":
            await send_telegram_message(chat_id, "👋 Welcome to Sofie! Ask me anything about Tanzanian aviation regulations.")
        elif text == "/help":
            await send_telegram_message(chat_id, "🤖 Just ask any question about Tanzanian aviation regulations!")
        else:
            # Process query
            logger.info(f"Making request to query endpoint with text: {text}")
            vercel_url = os.environ.get("VERCEL_URL")
            query_url = f"https://{vercel_url}/api/query"
            logger.info(f"Query URL: {query_url}")
            
            try:
                response = requests.post(query_url, json={"query": text})
                logger.info(f"Query response status: {response.status_code}")
                logger.info(f"Query response body: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    await send_telegram_message(chat_id, result["response"])
                else:
                    error_msg = f"Query endpoint error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    await send_telegram_message(chat_id, "❌ Sorry, I encountered an error processing your query.")
            except Exception as e:
                logger.error(f"Error making query request: {str(e)}")
                await send_telegram_message(chat_id, "❌ Internal error while processing query.")
        
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/webhook/test")
async def test_webhook():
    """Test endpoint to verify the webhook is running."""
    vercel_url = os.environ.get("VERCEL_URL")
    return {
        "status": "ok",
        "bot_token_set": bool(BOT_TOKEN),
        "vercel_url": vercel_url,
        "query_url": f"https://{vercel_url}/api/query" if vercel_url else None
    } 