import time
from typing import Dict, Any
from functools import wraps

def format_response(success: bool, message: str, data: Any = None) -> Dict[str, Any]:
    return {
        "success": success,
        "message": message,
        "data": data
    }

def validate_text(text: str, max_length: int = 4000) -> bool:
    if not text or len(text.strip()) == 0:
        return False
    if len(text) > max_length:
        return False
    return True

def rate_limit(max_calls: int = 10, time_frame: int = 60):
    """
    Decorator untuk rate limiting
    """
    calls = []
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_time = time.time()
            calls_in_timeframe = [call for call in calls if call > current_time - time_frame]
            
            if len(calls_in_timeframe) >= max_calls:
                raise Exception("Rate limit exceeded")
            
            calls.append(current_time)
            return await func(*args, **kwargs)
        return wrapper
    return decorator