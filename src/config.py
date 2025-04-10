from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # Google Drive settings
    regulations_folder_id: str = os.getenv("REGULATIONS_FOLDER_ID", "")
    
    # Telegram settings
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Vercel settings
    vercel_url: str = os.getenv("VERCEL_URL", "")

    class Config:
        env_file = ".env"

settings = Settings() 