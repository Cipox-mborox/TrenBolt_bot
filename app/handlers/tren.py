from telegram import Update
from telegram.ext import ContextTypes
from app.services.ai_analyzer import AIAnalyzer
import logging

logger = logging.getLogger(__name__)
ai_analyzer = AIAnalyzer()

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if not text or len(text.strip()) == 0:
        await update.message.reply_text("Silakan kirim teks yang ingin dianalisis.")
        return
    
    # Kirim pesan sedang memproses
    processing_msg = await update.message.reply_text("🔄 Menganalisis teks...")
    
    try:
        # Analisis dengan AI
        analysis = await ai_analyzer.analyze_text(text, user_id)
        
        # Hapus pesan processing
        await processing_msg.delete()
        
        # Kirim hasil analisis
        response_text = f"""
📊 **Hasil Analisis:**

**Input:** {text[:100]}...

**Analisis:**
{analysis}

💡 **Tips:** Gunakan fitur premium untuk analisis yang lebih mendalam!
        """
        
        await update.message.reply_text(response_text)
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        await processing_msg.delete()
        await update.message.reply_text("❌ Maaf, terjadi error saat menganalisis teks. Silakan coba lagi.")