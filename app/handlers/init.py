from .start import start, help_command
from .tren import handle_text
from .audio import handle_voice, handle_audio
from .premium import premium_info

# Import admin functions
try:
    from .admin import setup_admin_handlers, admin_panel
except ImportError as e:
    # Fallback jika admin.py tidak ada atau error
    def setup_admin_handlers(application):
        pass
    
    async def admin_panel(update, context):
        await update.message.reply_text("❌ Fitur admin sedang tidak tersedia.")

__all__ = [
    'start', 
    'help_command', 
    'handle_text', 
    'handle_voice', 
    'handle_audio', 
    'premium_info',
    'setup_admin_handlers',
    'admin_panel'
]