from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .knowledge_base import KnowledgeBase
from .config import settings

class TelegramBot:
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.application = Application.builder().token(settings.telegram_bot_token).build()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        welcome_message = (
            "👋 Welcome to Sofie, your Tanzanian Aviation Regulations Assistant!\n\n"
            "I can help you with questions about Tanzanian aviation regulations. "
            "Just ask your question, and I'll do my best to provide accurate information "
            "based on the latest regulations.\n\n"
            "Example questions:\n"
            "- What are the requirements for pilot licensing in Tanzania?\n"
            "- What are the safety regulations for commercial flights?\n"
            "- What are the procedures for aircraft registration?"
        )
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_message = (
            "🤖 How to use Sofie:\n\n"
            "1. Simply type your question about Tanzanian aviation regulations\n"
            "2. I'll search through the latest regulations and provide an answer\n"
            "3. If I'm not confident about an answer, I'll let you know\n\n"
            "Commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/update - Force update the knowledge base"
        )
        await update.message.reply_text(help_message)

    async def update_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /update command to force update the knowledge base."""
        await update.message.reply_text("🔄 Updating knowledge base...")
        try:
            self.knowledge_base.update_knowledge_base()
            await update.message.reply_text("✅ Knowledge base updated successfully!")
        except Exception as e:
            await update.message.reply_text(f"❌ Error updating knowledge base: {str(e)}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        query = update.message.text
        await update.message.reply_text("🔍 Searching for information...")

        try:
            response = self.knowledge_base.query_knowledge_base(query)
            answer = response['answer']
            confidence = response['confidence']

            if confidence < 0.5:
                answer += "\n\n⚠️ Note: I'm not entirely confident about this answer. Please verify the information in the official regulations."

            await update.message.reply_text(answer)
        except Exception as e:
            await update.message.reply_text(f"❌ Sorry, I encountered an error: {str(e)}")

    def setup(self):
        """Set up the bot handlers."""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("update", self.update_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def run(self):
        """Run the bot."""
        self.setup()
        self.application.run_polling() 