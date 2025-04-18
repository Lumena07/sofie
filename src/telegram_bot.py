from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from .config import settings

class TelegramBot:
    def __init__(self):
        self.client = OpenAI()
        self.assistant_id = settings.openai_assistant_id
        self.application = Application.builder().token(settings.telegram_bot_token).build()
        self.threads = {}  # Store threads for each user

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        welcome_message = (
            "👋 Welcome to Sofie, your Tanzanian Aviation Regulations Assistant!\n\n"
            "I can help you with questions about Tanzanian aviation regulations. "
            "Just ask your question, and I'll provide accurate information "
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
            "3. I'll include citations to the relevant regulations\n\n"
            "Commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message"
        )
        await update.message.reply_text(help_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        user_id = update.effective_user.id
        query = update.message.text
        
        # Create a new thread if this user doesn't have one
        if user_id not in self.threads:
            thread = self.client.beta.threads.create()
            self.threads[user_id] = thread.id
        
        await update.message.reply_text("🔍 Searching for information...")

        try:
            # Add message to thread
            message = self.client.beta.threads.messages.create(
                thread_id=self.threads[user_id],
                role="user",
                content=query
            )
            
            # Create and run
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.threads[user_id],
                assistant_id=self.assistant_id
            )
            
            # Get messages
            messages = list(self.client.beta.threads.messages.list(
                thread_id=self.threads[user_id],
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
                        cited_file = self.client.files.retrieve(file_citation.file_id)
                        citations.append(f"[{index}] {cited_file.filename}")
                
                # Send response
                response_text = f"{message_content.value}"
                if citations:
                    response_text += "\n\n📚 Citations:\n" + "\n".join(citations)
                
                await update.message.reply_text(response_text)
            else:
                await update.message.reply_text("❌ Sorry, I couldn't find any relevant information.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Sorry, I encountered an error: {str(e)}")

    def setup(self):
        """Set up the bot handlers."""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def run(self):
        """Run the bot."""
        self.setup()
        self.application.run_polling() 