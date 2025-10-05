from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def premium_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    premium_text = """
🌟 **Fitur Premium Trenbolt-Bot**

**Fitur yang didapat:**
✅ Analisis tren yang lebih mendalam
✅ Transkripsi audio tanpa batas
✅ Akses ke model AI terbaru
✅ Prioritas pemrosesan
✅ Support 24/7

**Harga:**
• Bulanan: Rp 50.000/bulan
• Tahunan: Rp 500.000/tahun

**Cara berlangganan:**
Kirim permintaan ke @admin untuk info lebih lanjut.

💎 **Upgrade sekarang dan tingkatkan produktivitas Anda!**
    """
    
    await update.message.reply_text(premium_text)