from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load .env file untuk development
load_dotenv()

# Check environment variables (opsional)
try:
    from app.utils.check_env import check_environment_variables
    check_environment_variables()
except ImportError:
    logger.warning("utils.check_env tidak tersedia")