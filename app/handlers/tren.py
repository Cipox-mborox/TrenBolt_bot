from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if not text or len(text.strip()) == 0:
        await update.message.reply_text("Silakan kirim teks yang ingin dianalisis.")
        return
    
    # Kirim pesan sedang memproses
    processing_msg = await update.message.reply_text("🔄 Menganalisis teks...")
    
    try:
        # Analisis sederhana tanpa AI
        analysis = f"""
📊 **Hasil Analisis Sederhana:**

**Input:** {text[:100]}...

**Kata-kata kunci:** {', '.join(set(text.split()[:5]))}
**Panjang teks:** {len(text)} karakter
**Jumlah kata:** {len(text.split())}

💡 **Tips:** Fitur AI sedang dalam pengembangan. 
Gunakan /premium untuk info fitur lengkap.
        """
        
        await processing_msg.delete()
        await update.message.reply_text(analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        await processing_msg.delete()
        await update.message.reply_text("❌ Maaf, terjadi error saat menganalisis teks.")