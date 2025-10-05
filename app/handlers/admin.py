import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

logger = logging.getLogger(__name__)

# List admin user IDs
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]

def admin_required(func):
    """Decorator untuk membatasi akses hanya untuk admin"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Akses ditolak. Hanya admin yang dapat menggunakan perintah ini.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

@admin_required
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Panel utama admin"""
    keyboard = [
        [InlineKeyboardButton("📊 Statistik Bot", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Manage Users", callback_data="admin_users")],
        [InlineKeyboardButton("🔧 Broadcast", callback_data="admin_broadcast")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🛠️ **Admin Panel**\n\n"
        "Pilih opsi di bawah:",
        reply_markup=reply_markup
    )

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback dari admin panel"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Akses ditolak.")
        return
    
    data = query.data
    
    if data == "admin_stats":
        await show_bot_stats(query, context)
    elif data == "admin_back":
        await admin_panel_back(query, context)
    else:
        await query.edit_message_text("⚠️ Fitur ini sedang dalam pengembangan.")

async def show_bot_stats(query, context):
    """Menampilkan statistik bot sederhana"""
    try:
        text = """
📊 **Statistik Bot**

👥 **Total Users:** Data tidak tersedia
🚀 **Active Users:** Data tidak tersedia
📨 **Total Usage:** Data tidak tersedia

💡 *Database sedang dalam pengembangan*
        """
        
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await query.edit_message_text("❌ Error mengambil statistik.")

async def admin_panel_back(query, context):
    """Kembali ke admin panel"""
    await admin_panel(update=query, context=context)

def setup_admin_handlers(application):
    """Setup semua handler admin"""
    try:
        application.add_handler(CommandHandler("admin", admin_panel))
        application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^admin_"))
        logger.info("✅ Admin handlers berhasil di-setup")
    except Exception as e:
        logger.error(f"❌ Error setup admin handlers: {e}")