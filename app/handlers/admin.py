import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from app.services.database import get_user, get_all_users, get_usage_stats, update_user_premium
from app.services.ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)

# List admin user IDs (isi dengan user ID Telegram admin)
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
        [InlineKeyboardButton("💰 Manage Premium", callback_data="admin_premium")],
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
    elif data == "admin_users":
        await show_users_management(query, context)
    elif data == "admin_broadcast":
        await start_broadcast(query, context)
    elif data == "admin_premium":
        await show_premium_management(query, context)
    elif data.startswith("user_detail_"):
        user_id = int(data.split("_")[2])
        await show_user_detail(query, context, user_id)
    elif data.startswith("premium_toggle_"):
        user_id = int(data.split("_")[2])
        await toggle_premium(query, context, user_id)
    elif data == "admin_back":
        await admin_panel_back(query, context)

async def show_bot_stats(query, context):
    """Menampilkan statistik bot"""
    try:
        stats = await get_usage_stats()
        
        text = f"""
📊 **Statistik Bot**

👥 **Total Users:** {stats['total_users']}
🚀 **Active Users (30 hari):** {stats['active_users']}
💎 **Premium Users:** {stats['premium_users']}
📨 **Total Usage:** {stats['total_usage']}

📈 **Usage Hari Ini:** {stats['today_usage']}
📅 **Usage Bulan Ini:** {stats['month_usage']}
        """
        
        keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats")],
                   [InlineKeyboardButton("⬅️ Back", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await query.edit_message_text("❌ Error mengambil statistik.")

async def show_users_management(query, context):
    """Menampilkan manajemen users"""
    try:
        users = await get_all_users(limit=10)
        
        text = "👥 **Manajemen Users**\n\n"
        keyboard = []
        
        for user in users:
            premium_status = "💎" if user['is_premium'] else "🔹"
            text += f"{premium_status} {user['user_id']} - {user['first_name']} (Usage: {user['usage_count']})\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"👤 {user['first_name']}",
                    callback_data=f"user_detail_{user['user_id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        await query.edit_message_text("❌ Error mengambil data users.")

async def show_user_detail(query, context, user_id):
    """Menampilkan detail user"""
    try:
        user = await get_user(user_id)
        
        if not user:
            await query.edit_message_text("❌ User tidak ditemukan.")
            return
        
        premium_status = "Aktif 💎" if user['is_premium'] else "Tidak Aktif 🔹"
        text = f"""
👤 **Detail User**

🆔 **User ID:** {user['user_id']}
👤 **Nama:** {user['first_name']} {user['last_name'] or ''}
📛 **Username:** @{user['username'] or 'Tidak ada'}
💎 **Premium:** {premium_status}
📊 **Total Usage:** {user['usage_count']}
📅 **Bergabung:** {user['created_at'].strftime('%Y-%m-%d %H:%M')}
        """
        
        keyboard = [
            [InlineKeyboardButton(f"🔄 Toggle Premium", callback_data=f"premium_toggle_{user['user_id']}")],
            [InlineKeyboardButton("⬅️ Back to Users", callback_data="admin_users")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting user detail: {e}")
        await query.edit_message_text("❌ Error mengambil detail user.")

async def toggle_premium(query, context, user_id):
    """Toggle status premium user"""
    try:
        user = await get_user(user_id)
        if not user:
            await query.edit_message_text("❌ User tidak ditemukan.")
            return
        
        new_status = not user['is_premium']
        await update_user_premium(user_id, new_status)
        
        status_text = "diaktifkan" if new_status else "dinonaktifkan"
        await query.edit_message_text(f"✅ Status premium user {user_id} {status_text}.")
        
        # Kembali ke detail user
        await show_user_detail(query, context, user_id)
        
    except Exception as e:
        logger.error(f"Error toggling premium: {e}")
        await query.edit_message_text("❌ Error mengubah status premium.")

async def start_broadcast(query, context):
    """Memulai broadcast message"""
    context.user_data['awaiting_broadcast'] = True
    text = """
📢 **Broadcast Message**

Ketik pesan yang ingin di-broadcast ke semua users:

**Formatting:**
- Gunakan HTML formatting
- <b>Bold</b>
- <i>Italic</i>
- <code>Monospace</code>

**Cancel:** ketik /cancel
    """
    
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_premium_management(query, context):
    """Menampilkan manajemen premium"""
    text = """
💰 **Manajemen Premium**

Fitur:
• Toggle status premium user
• Lihat user premium
• Manage subscriptions

Gunakan menu Users untuk manage individual user.
    """
    
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def admin_panel_back(query, context):
    """Kembali ke admin panel"""
    await admin_panel(update=query, context=context)

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast message dari admin"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return
    
    if not context.user_data.get('awaiting_broadcast'):
        return
    
    message_text = update.message.text
    context.user_data['awaiting_broadcast'] = False
    
    # Konfirmasi broadcast
    keyboard = [
        [InlineKeyboardButton("✅ Ya, Broadcast", callback_data="confirm_broadcast")],
        [InlineKeyboardButton("❌ Batal", callback_data="cancel_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data['pending_broadcast'] = message_text
    
    await update.message.reply_text(
        f"📢 **Konfirmasi Broadcast**\n\n"
        f"Pesan:\n{message_text}\n\n"
        f"Kirim ke semua users?",
        reply_markup=reply_markup
    )

async def handle_broadcast_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle konfirmasi broadcast"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in ADMIN_IDS:
        return
    
    data = query.data
    
    if data == "confirm_broadcast":
        message_text = context.user_data.get('pending_broadcast')
        if message_text:
            await send_broadcast(context, message_text, query)
        else:
            await query.edit_message_text("❌ Tidak ada pesan untuk di-broadcast.")
    
    elif data == "cancel_broadcast":
        context.user_data.pop('pending_broadcast', None)
        await query.edit_message_text("❌ Broadcast dibatalkan.")

async def send_broadcast(context, message_text, query):
    """Mengirim broadcast ke semua users"""
    try:
        await query.edit_message_text("🔄 Mengirim broadcast...")
        
        users = await get_all_users()
        success_count = 0
        fail_count = 0
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user['user_id'],
                    text=message_text,
                    parse_mode='HTML'
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send to {user['user_id']}: {e}")
                fail_count += 1
        
        await query.edit_message_text(
            f"✅ **Broadcast Selesai**\n\n"
            f"✅ Berhasil: {success_count}\n"
            f"❌ Gagal: {fail_count}\n"
            f"📊 Total: {success_count + fail_count}"
        )
        
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        await query.edit_message_text("❌ Error saat broadcast.")

@admin_required
async def admin_export_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export data users ke CSV"""
    try:
        users = await get_all_users()
        
        # Buat CSV content
        csv_content = "User ID,Username,First Name,Last Name,Premium,Usage Count,Created At\n"
        for user in users:
            csv_content += f"{user['user_id']},{user['username'] or ''},{user['first_name']},{user['last_name'] or ''},{user['is_premium']},{user['usage_count']},{user['created_at']}\n"
        
        # Kirim sebagai file
        await update.message.reply_document(
            document=csv_content.encode(),
            filename="users_export.csv",
            caption="📊 Export Data Users"
        )
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        await update.message.reply_text("❌ Error export data.")

def setup_admin_handlers(application):
    """Setup semua handler admin"""
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^admin_"))
    application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^user_detail_"))
    application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^premium_toggle_"))
    application.add_handler(CallbackQueryHandler(handle_broadcast_confirmation, pattern="^(confirm_broadcast|cancel_broadcast)$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_message))
    application.add_handler(CommandHandler("export_users", admin_export_users))