from telegram import Update
from telegram.ext import ContextTypes
import logging
import os

logger = logging.getLogger(__name__)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if not text or len(text.strip()) == 0:
        await update.message.reply_text("Silakan kirim teks yang ingin dianalisis.")
        return
    
    # Cek apakah AI tersedia
    ai_available = bool(os.getenv('GOOGLE_AI_STUDIO_API_KEY'))
    
    if not ai_available:
        # Analisis sederhana tanpa AI
        await analyze_text_basic(update, text)
    else:
        # Analisis dengan AI
        await analyze_text_ai(update, text, user_id)

async def analyze_text_basic(update: Update, text: str):
    """Analisis teks sederhana tanpa AI"""
    processing_msg = await update.message.reply_text("📊 Menganalisis teks...")
    
    try:
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        # Analisis sederhana
        analysis = f"""
📊 **Hasil Analisis Dasar:**

**Input:** {text[:100]}...

📈 **Statistik:**
• Panjang teks: {char_count} karakter
• Jumlah kata: {word_count} kata
• Kata terpanjang: {max(words, key=len) if words else 'N/A'}
• Rata-rata panjang kata: {sum(len(word) for word in words) // word_count if word_count > 0 else 0} karakter

🔍 **Kata-kata kunci:** {', '.join(set(words[:8]))}

⚠️ **Fitur AI Tidak Aktif**
💡 *Admin perlu mengonfigurasi Google AI Studio API Key untuk analisis AI.*
        """
        
        await processing_msg.delete()
        await update.message.reply_text(analysis)
        
    except Exception as e:
        logger.error(f"Error in basic analysis: {e}")
        await processing_msg.delete()
        await update.message.reply_text("❌ Maaf, terjadi error saat menganalisis teks.")

async def analyze_text_ai(update: Update, text: str, user_id: int):
    """Analisis teks dengan AI"""
    processing_msg = await update.message.reply_text("🧠 Menganalisis dengan AI...")
    
    try:
        from app.services.ai_analyzer import AIAnalyzer
        ai_analyzer = AIAnalyzer()
        
        if not ai_analyzer.is_enabled:
            await processing_msg.delete()
            await update.message.reply_text("❌ AI tidak aktif. Beralih ke analisis dasar...")
            await analyze_text_basic(update, text)
            return
        
        analysis = await ai_analyzer.analyze_text(text, user_id)
        
        await processing_msg.delete()
        
        # Format response
        if analysis.startswith("❌"):
            # Jika ada error, fallback ke basic analysis
            await update.message.reply_text(f"{analysis}\n\nBeralih ke analisis dasar...")
            await analyze_text_basic(update, text)
        else:
            # Potong teks jika terlalu panjang untuk Telegram
            if len(analysis) > 4000:
                analysis = analysis[:4000] + "\n\n... (pesan dipotong karena terlalu panjang)"
            
            response_text = f"""
🤖 **Hasil Analisis AI:**

{analysis}

💎 *Dianalisis dengan Google Gemini AI*
            """
            await update.message.reply_text(response_text)
        
    except Exception as e:
        logger.error(f"AI Analysis error: {e}")
        try:
            await processing_msg.delete()
        except:
            pass
        await update.message.reply_text("❌ Error pada analisis AI. Beralih ke analisis dasar...")
        await analyze_text_basic(update, text)