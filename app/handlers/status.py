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
    
    # Test AI connection
    ai_status = "❌ Tidak aktif"
    ai_detail = "Belum di-test"
    
    if google_api_key:
        try:
            from app.services.ai_analyzer import AIAnalyzer
            analyzer = AIAnalyzer()
            
            if analyzer.is_enabled:
                ai_status = "✅ Aktif"
                ai_detail = "Model: gemini-2.0-flash"
            else:
                ai_status = "❌ Error"
                ai_detail = "Gagal inisialisasi AI"
                
        except Exception as e:
            ai_status = "❌ Error"
            ai_detail = f"Error: {str(e)}"
    
    status_text = f"""
🔧 **Status Sistem Trenbolt-Bot**

🤖 **Telegram Bot:** {'✅ OK' if telegram_token else '❌ Error'}
🧠 **Google AI Studio:** {ai_status}
📋 **Detail AI:** {ai_detail}

💡 **Commands:**
/start - Memulai bot
/testai - Test AI
/status - Status sistem
"""
    
    await update.message.reply_text(status_text)

async def test_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test AI dengan prompt sederhana"""
    test_text = "Halo, ini adalah test AI. Bisakah kamu memperkenalkan diri dalam 2-3 kalimat?"
    
    processing_msg = await update.message.reply_text("🧠 Testing AI...")
    
    try:
        from app.services.ai_analyzer import AIAnalyzer
        analyzer = AIAnalyzer()
        
        if not analyzer.is_enabled:
            await processing_msg.delete()
            await update.message.reply_text("❌ AI tidak aktif.")
            return
        
        response = await analyzer.analyze_text(test_text, update.effective_user.id)
        
        await processing_msg.delete()
        
        if response.startswith("❌"):
            result_text = f"""
🧪 **AI Test Result:**

**Status:** ❌ AI Error
**Error:** {response}
"""
        else:
            result_text = f"""
🧪 **AI Test Result:**

**Prompt:** {test_text}

**Response:**
{response}

**Status:** ✅ AI BERHASIL!
"""
        await update.message.reply_text(result_text)
        
    except Exception as e:
        await processing_msg.delete()
        await update.message.reply_text(f"❌ AI Test Failed:\n{str(e)}")

def setup_status_handlers(application):
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("testai", test_ai_command))