import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TrenboltBot:
    def __init__(self):
        # Cek environment variables
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.google_api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
        
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN tidak ditemukan!")
            raise ValueError("TELEGRAM_BOT_TOKEN tidak ditemukan!")
        
        if not self.google_api_key:
            logger.warning("⚠️ GOOGLE_AI_STUDIO_API_KEY tidak ditemukan. Fitur AI akan dinonaktifkan.")
        
        self.application = Application.builder().token(self.token).build()
        
        # Import handlers secara manual untuk menghindari circular imports
        from app.handlers.start import start, help_command
        from app.handlers.tren import handle_text
        from app.handlers.audio import handle_voice, handle_audio
        from app.handlers.premium import premium_info
        
        self.handlers = {
            'start': start,
            'help_command': help_command,
            'handle_text': handle_text,
            'handle_voice': handle_voice,
            'handle_audio': handle_audio,
            'premium_info': premium_info
        }
        
    def setup_handlers(self):
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handlers['start']))
        self.application.add_handler(CommandHandler("help", self.handlers['help_command']))
        self.application.add_handler(CommandHandler("premium", self.handlers['premium_info']))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers['handle_text']))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handlers['handle_voice']))
        self.application.add_handler(MessageHandler(filters.AUDIO, self.handlers['handle_audio']))
        
        # Admin handlers
        try:
            from app.handlers import setup_admin_handlers
            setup_admin_handlers(self.application)
        except ImportError as e:
            logger.warning(f"⚠️ Admin handlers tidak dapat di-load: {e}")
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def error_handler(self, update, context):
        logger.error(msg="Exception occurred:", exc_info=context.error)
    
    def run(self):
        self.setup_handlers()
        logger.info("🤖 Trenbolt-Bot sedang berjalan...")
        
        # Untuk production di Railway
        port = int(os.environ.get('PORT', 8443))
        webhook_url = os.getenv('RAILWAY_STATIC_URL')
        
        if webhook_url:
            # Production mode dengan webhook
            logger.info(f"🌐 Production mode dengan webhook: {webhook_url}")
            self.application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=self.token,
                webhook_url=f"{webhook_url}/{self.token}"
            )
        else:
            # Development mode dengan polling
            logger.info("🔧 Development mode dengan polling")
            self.application.run_polling()

def main():
    """Main function dengan error handling"""
    try:
        # Initialize dan run bot
        bot = TrenboltBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        logger.info("💡 Pastikan environment variables sudah di-set dengan benar:")
        logger.info("   - TELEGRAM_BOT_TOKEN")
        logger.info("   - GOOGLE_AI_STUDIO_API_KEY (opsional)")

if __name__ == '__main__':
    main()