from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .telegram_bot import TelegramBot
from .config import settings
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize bot
try:
    bot = TelegramBot()
    logger.info("Telegram bot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Telegram bot: {str(e)}")
    bot = None

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook requests from Telegram."""
    if not bot:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Telegram bot not initialized"}
        )
    
    try:
        data = await request.json()
        update = json.loads(data)
        logger.info(f"Received webhook update: {update}")
        
        # Process the update
        await bot.application.process_update(update)
        
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        if not bot:
            return JSONResponse(
                status_code=500,
                content={"status": "unhealthy", "message": "Telegram bot not initialized"}
            )
        return {"status": "healthy", "bot": "initialized"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "message": str(e)}
        )

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 