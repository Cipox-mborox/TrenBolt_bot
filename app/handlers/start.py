from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""
🤖 Halo {user.first_name}! Selamat datang di Trenbolt-Bot!

Saya adalah asisten AI yang dapat membantu Anda:
• Menganalisis tren dan konten
• Memproses audio menjadi teks
• Memberikan insights berdasarkan data terkini

🔧 **Fitur yang tersedia:**
/text - Analisis teks dengan AI
/audio - Konversi suara ke teks
/premium - Info fitur premium

Coba kirim saya pesan teks atau audio!
    """
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 **Bantuan Trenbolt-Bot**

**Perintah yang tersedia:**
/start - Memulai bot
/help - Menampilkan bantuan ini
/premium - Info fitur premium

**Cara menggunakan:**
1. Kirim teks langsung untuk dianalisis
2. Kirim pesan suara untuk dikonversi ke teks
3. Gunakan fitur premium untuk analisis mendalam
    """
    
    await update.message.reply_text(help_text)