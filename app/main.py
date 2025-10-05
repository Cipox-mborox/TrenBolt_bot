import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.handlers import start, tren, audio, premium, setup_admin_handlers
from app.services.database import init_db
from app.services.ai_analyzer import AIAnalyzer

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TrenboltBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN tidak ditemukan!")
        
        self.application = Application.builder().token(self.token).build()
        self.ai_analyzer = AIAnalyzer()
        
    def setup_handlers(self):
        # Command handlers
        self.application.add_handler(CommandHandler("start", start.start))
        self.application.add_handler(CommandHandler("help", start.help_command))
        self.application.add_handler(CommandHandler("premium", premium.premium_info))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tren.handle_text))
        self.application.add_handler(MessageHandler(filters.VOICE, audio.handle_voice))
        self.application.add_handler(MessageHandler(filters.AUDIO, audio.handle_audio))
        
        # Admin handlers
        setup_admin_handlers(self.application)
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def error_handler(self, update, context):
        logger.error(msg="Exception occurred:", exc_info=context.error)
    
    def run(self):
        self.setup_handlers()
        logger.info("Bot sedang berjalan...")
        
        # Untuk production di Railway
        port = int(os.environ.get('PORT', 8443))
        webhook_url = os.getenv('RAILWAY_STATIC_URL')
        
        if webhook_url:
            # Production mode dengan webhook
            self.application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=self.token,
                webhook_url=f"{webhook_url}/{self.token}"
            )
        else:
            # Development mode dengan polling
            self.application.run_polling()

async def init_app():
    await init_db()
    bot = TrenboltBot()
    return bot

if __name__ == '__main__':
    import asyncio
    bot = asyncio.run(init_app())
    bot.run()