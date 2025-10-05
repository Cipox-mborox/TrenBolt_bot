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
    
    # Test AI connection dengan detail
    ai_status = "❌ Tidak aktif"
    ai_detail = "Belum di-test"
    
    if google_api_key:
        try:
            from app.services.ai_analyzer import AIAnalyzer
            analyzer = AIAnalyzer()
            
            if analyzer.is_enabled:
                ai_status = "✅ Aktif"
                ai_detail = "Model berhasil di-load"
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
/status - Status sistem
/testai - Test AI
/testmodel - Test model tersedia
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

async def test_model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test model availability"""
    
    processing_msg = await update.message.reply_text("🔍 Checking available models...")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_AI_STUDIO_API_KEY'))
        
        models = genai.list_models()
        available_models = [model.name for model in models]
        
        model_list = "\n".join([f"• {model}" for model in available_models[:10]])  # Show first 10
        
        result_text = f"""
📋 **Available Models:** {len(available_models)}

{model_list}

{"..." if len(available_models) > 10 else ""}

✅ **Status:** Model list berhasil
"""
        await processing_msg.delete()
        await update.message.reply_text(result_text)
        
    except Exception as e:
        await processing_msg.delete()
        await update.message.reply_text(f"❌ Error getting models: {str(e)}")

def setup_status_handlers(application):
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("testai", test_ai_command))
    application.add_handler(CommandHandler("testmodel", test_model_command))