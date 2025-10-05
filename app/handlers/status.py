from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import os
import logging

logger = logging.getLogger(__name__)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cek status AI dan sistem"""
    
    # Cek environment variables
    telegram_token = bool(os.getenv('TELEGRAM_BOT_TOKEN'))
    google_api_key = bool(os.getenv('GOOGLE_AI_STUDIO_API_KEY'))
    admin_ids = os.getenv('ADMIN_IDS')
    database_url = bool(os.getenv('DATABASE_URL'))
    
    # Test AI connection
    ai_status = "❌ Tidak aktif"
    ai_test_result = "Belum di-test"
    
    if google_api_key:
        try:
            from app.services.ai_analyzer import AIAnalyzer
            analyzer = AIAnalyzer()
            if analyzer.is_enabled:
                ai_status = "✅ Aktif"
                # Test simple AI call
                test_response = await analyzer.analyze_text("Test", update.effective_user.id)
                ai_test_result = "✅ Berhasil terhubung"
            else:
                ai_status = "❌ Error konfigurasi"
                ai_test_result = "Gagal inisialisasi AI"
        except Exception as e:
            ai_status = "❌ Error"
            ai_test_result = f"Error: {str(e)}"
    
    status_text = f"""
🔧 **Status Sistem Trenbolt-Bot**

🤖 **Telegram Bot:** {'✅ OK' if telegram_token else '❌ Error'}
🧠 **Google AI Studio:** {ai_status}
📊 **Test AI:** {ai_test_result}
💾 **Database:** {'✅ OK' if database_url else '❌ Tidak ada'}
👥 **Admin IDs:** {admin_ids if admin_ids else 'Tidak di-set'}

📝 **Environment Variables:**
• TELEGRAM_BOT_TOKEN: {'✅' if telegram_token else '❌'}
• GOOGLE_AI_STUDIO_API_KEY: {'✅' if google_api_key else '❌'}
• ADMIN_IDS: {'✅' if admin_ids else '❌'}
• DATABASE_URL: {'✅' if database_url else '❌'}

💡 **Tips:** Gunakan /testai untuk test AI langsung
    """
    
    await update.message.reply_text(status_text)

async def test_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test AI dengan prompt sederhana"""
    test_text = "Halo, ini adalah test AI. Bisakah kamu memperkenalkan diri?"
    
    processing_msg = await update.message.reply_text("🧠 Testing AI...")
    
    try:
        from app.services.ai_analyzer import AIAnalyzer
        analyzer = AIAnalyzer()
        
        if not analyzer.is_enabled:
            await processing_msg.delete()
            await update.message.reply_text("❌ AI tidak aktif. Cek /status untuk detail.")
            return
        
        response = await analyzer.analyze_text(test_text, update.effective_user.id)
        
        await processing_msg.delete()
        
        result_text = f"""
🧪 **Test AI Result:**

**Prompt:** {test_text}

**Response:**
{response}

**Status:** ✅ AI Berfungsi
"""
        await update.message.reply_text(result_text)
        
    except Exception as e:
        await processing_msg.delete()
        await update.message.reply_text(f"❌ AI Test Failed:\n{str(e)}")

def setup_status_handlers(application):
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("testai", test_ai_command))