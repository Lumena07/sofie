from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import os
import logging
import requests
import sys
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI()
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.environ.get("OPENAI_ASSISTANT_ID")

# Log environment variables (without sensitive values)
logger.info(f"Environment variables loaded: BOT_TOKEN={bool(BOT_TOKEN)}, OPENAI_API_KEY={bool(OPENAI_API_KEY)}, OPENAI_ASSISTANT_ID={bool(OPENAI_ASSISTANT_ID)}")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Store threads for each chat
threads = {}

async def send_telegram_message(chat_id: int, text: str):
    """Send a message using Telegram API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    logger.info(f"Sending message to chat {chat_id}: {text[:100]}...")
    response = requests.post(url, json=data)
    if not response.ok:
        logger.error(f"Failed to send message: {response.status_code} - {response.text}")
    else:
        logger.info(f"Message sent successfully to chat {chat_id}")

def get_or_create_thread(chat_id: int) -> str:
    """Get existing thread or create a new one for the chat."""
    if chat_id not in threads:
        thread = client.beta.threads.create()
        threads[chat_id] = thread.id
        logger.info(f"Created new thread {thread.id} for chat {chat_id}")
    return threads[chat_id]

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook requests from Telegram."""
    try:
        data = await request.json()
        logger.info(f"Received webhook data: {json.dumps(data)[:200]}...")
        
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        logger.info(f"Processing message: chat_id={chat_id}, text={text}")
        
        if not chat_id:
            logger.error("No chat_id found in message")
            return JSONResponse(status_code=400, content={"error": "No chat_id found"})
            
        if text == "/start":
            logger.info(f"Handling /start command for chat {chat_id}")
            await send_telegram_message(chat_id, "👋 Welcome to Sofie! Ask me anything about Tanzanian aviation regulations.")
        elif text == "/help":
            logger.info(f"Handling /help command for chat {chat_id}")
            await send_telegram_message(chat_id, "🤖 Just ask any question about Tanzanian aviation regulations!")
        else:
            # Process query using OpenAI Assistant
            try:
                logger.info(f"Processing query for chat {chat_id}: {text}")
                # Get or create thread for this chat
                thread_id = get_or_create_thread(chat_id)
                
                # Add message to thread
                message = client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=text
                )
                
                # Create and run
                run = client.beta.threads.runs.create_and_poll(
                    thread_id=thread_id,
                    assistant_id=OPENAI_ASSISTANT_ID
                )
                
                # Get messages
                messages = list(client.beta.threads.messages.list(
                    thread_id=thread_id,
                    run_id=run.id
                ))
                
                # Process response with citations
                if messages:
                    message_content = messages[0].content[0].text
                    annotations = message_content.annotations
                    citations = []
                    
                    for index, annotation in enumerate(annotations):
                        message_content.value = message_content.value.replace(
                            annotation.text, f"[{index}]"
                        )
                        if file_citation := getattr(annotation, "file_citation", None):
                            cited_file = client.files.retrieve(file_citation.file_id)
                            citations.append(f"[{index}] {cited_file.filename}")
                    
                    # Send response
                    response_text = f"{message_content.value}"
                    if citations:
                        response_text += "\n\n📚 Citations:\n" + "\n".join(citations)
                    
                    logger.info(f"Sending response to chat {chat_id}: {response_text[:100]}...")
                    await send_telegram_message(chat_id, response_text)
                else:
                    logger.warning(f"No messages found for chat {chat_id}")
                    await send_telegram_message(chat_id, "❌ Sorry, I couldn't find any relevant information.")
                    
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                await send_telegram_message(chat_id, "❌ Sorry, I encountered an error processing your query.")
        
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
    return {
        "status": "ok",
        "bot_token_set": bool(BOT_TOKEN),
        "openai_api_key_set": bool(OPENAI_API_KEY),
        "assistant_id_set": bool(OPENAI_ASSISTANT_ID)
    } 