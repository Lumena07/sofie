from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .telegram_bot import TelegramBot
from .config import settings
import json

app = FastAPI()
bot = TelegramBot()

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook requests from Telegram."""
    try:
        data = await request.json()
        update = json.loads(data)
        
        # Process the update
        await bot.application.process_update(update)
        
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 