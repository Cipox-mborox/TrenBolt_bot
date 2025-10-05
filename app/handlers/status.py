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
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GOOGLE_AI_STUDIO_API_KEY'))
            
            # List available models
            models = genai.list_models()
            available_models = [model.name for model in models]
            
            ai_status = "✅ Aktif"
            ai_detail = f"Model tersedia: {len(available_models)}"
            
            # Show first few models
            if available_models:
                ai_detail += f"\n• {available_models[0]}"
                if len(available_models) > 1:
                    ai_detail += f"\n• {available_models[1]}"
                if len(available_models) > 2:
                    ai_detail += f"\n• ... dan {len(available_models)-2} lainnya"
                    
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