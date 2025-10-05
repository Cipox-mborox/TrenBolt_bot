import os
import logging

logger = logging.getLogger(__name__)

def check_environment_variables():
    """Check semua environment variables yang diperlukan"""
    variables = {
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'GOOGLE_AI_STUDIO_API_KEY': os.getenv('GOOGLE_AI_STUDIO_API_KEY'),
        'ADMIN_IDS': os.getenv('ADMIN_IDS'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'RAILWAY_STATIC_URL': os.getenv('RAILWAY_STATIC_URL'),
    }
    
    for key, value in variables.items():
        if value:
            logger.info(f"✅ {key}: ***{value[-4:]}" if len(value) > 4 else "***")
        else:
            logger.warning(f"❌ {key}: TIDAK DI-SET")
    
    return variables