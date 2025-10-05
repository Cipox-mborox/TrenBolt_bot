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
        
        logger.info(f"✅ TELEGRAM_BOT_TOKEN: {'***' + self.token[-4:] if self.token else 'MISSING'}")
        logger.info(f"✅ GOOGLE_AI_STUDIO_API_KEY: {'SET' if self.google_api_key else 'MISSING'}")
        
        self.application = Application.builder().token(self.token).build()
        
    def setup_handlers(self):
        """Setup semua handlers dengan import langsung"""
        try:
            from app.handlers.start import start, help_command
            from app.handlers.tren import handle_text
            from app.handlers.audio import handle_voice, handle_audio
            from app.handlers.premium import premium_info
            
            # Command handlers
            self.application.add_handler(CommandHandler("start", start))
            self.application.add_handler(CommandHandler("help", help_command))
            self.application.add_handler(CommandHandler("premium", premium_info))
            
            # Message handlers
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
            self.application.add_handler(MessageHandler(filters.VOICE, handle_voice))
            self.application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
            
            logger.info("✅ Basic handlers berhasil di-setup")
            
        except ImportError as e:
            logger.error(f"❌ Error import basic handlers: {e}")
            raise
        
        # Setup admin handlers (opsional)
        self.setup_admin_handlers()
        
        # Setup status handlers
        self.setup_status_handlers()
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    def setup_admin_handlers(self):
        """Setup admin handlers dengan error handling"""
        try:
            from app.handlers.admin import setup_admin_handlers
            setup_admin_handlers(self.application)
            logger.info("✅ Admin handlers berhasil di-setup")
        except ImportError as e:
            logger.warning(f"⚠️ Admin handlers tidak dapat di-load: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Error setup admin handlers: {e}")
    
    def setup_status_handlers(self):
        """Setup status handlers"""
        try:
            from app.handlers.status import setup_status_handlers
            setup_status_handlers(self.application)
            logger.info("✅ Status handlers berhasil di-setup")
        except ImportError as e:
            logger.warning(f"⚠️ Status handlers tidak dapat di-load: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Error setup status handlers: {e}")
    
    async def error_handler(self, update, context):
        logger.error(msg="Exception occurred:", exc_info=context.error)
    
    def run(self):
        self.setup_handlers()
        logger.info("🤖 Trenbolt-Bot sedang berjalan...")
        
        # Log AI status
        if self.google_api_key:
            try:
                from app.services.ai_analyzer import AIAnalyzer
                analyzer = AIAnalyzer()
                if analyzer.is_enabled:
                    logger.info("✅ Google AI Studio: AKTIF")
                else:
                    logger.error("❌ Google AI Studio: GAGAL INISIALISASI")
            except Exception as e:
                logger.error(f"❌ Error checking AI status: {e}")
        else:
            logger.warning("⚠️ Google AI Studio: API KEY TIDAK ADA")
        
        # Untuk production di Railway
        port = int(os.environ.get('PORT', 8443))
        webhook_url = os.getenv('RAILWAY_STATIC_URL')
        
        if webhook_url and self.token:
            logger.info(f"🌐 Production mode dengan webhook: {webhook_url}")
            try:
                self.application.run_webhook(
                    listen="0.0.0.0",
                    port=port,
                    url_path=self.token,
                    webhook_url=f"{webhook_url}/{self.token}"
                )
            except Exception as e:
                logger.error(f"❌ Webhook error: {e}")
                logger.info("🔄 Fallback ke polling mode...")
                self.application.run_polling()
        else:
            logger.info("🔧 Development mode dengan polling")
            self.application.run_polling()

def main():
    """Main function dengan error handling"""
    try:
        bot = TrenboltBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")

if __name__ == '__main__':
    main()