import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
        
        logger.info(f"🔧 Initializing AI Analyzer...")
        logger.info(f"🔧 API Key available: {bool(api_key)}")
        
        if not api_key:
            logger.warning("⚠️ GOOGLE_AI_STUDIO_API_KEY tidak ditemukan. Fitur AI dinonaktifkan.")
            self.model = None
            self.is_enabled = False
            return
        
        try:
            import google.generativeai as genai
            logger.info("✅ google.generativeai imported successfully")
            
            # Configure dengan error handling lebih detail
            genai.configure(api_key=api_key)
            logger.info("✅ Google AI configured")
            
            # List available models untuk debugging
            try:
                models = genai.list_models()
                available_models = [model.name for model in models]
                logger.info(f"📋 Available models: {available_models}")
            except Exception as e:
                logger.warning(f"⚠️ Cannot list models: {e}")
            
            # Coba beberapa model yang mungkin tersedia
            model_name = None
            possible_models = [
                'models/gemini-1.5-pro',
                'models/gemini-1.5-flash', 
                'models/gemini-pro',
                'models/gemini-pro-vision',
                'models/gemini-1.0-pro'
            ]
            
            for model in possible_models:
                try:
                    self.model = genai.GenerativeModel(model)
                    model_name = model
                    logger.info(f"✅ Using model: {model}")
                    break
                except Exception as e:
                    logger.warning(f"❌ Model {model} not available: {e}")
                    continue
            
            if not model_name:
                # Fallback ke model default atau coba tanpa specify model
                try:
                    self.model = genai.GenerativeModel()
                    logger.info("✅ Using default model")
                except Exception as e:
                    logger.error(f"❌ No model available: {e}")
                    raise
            
            self.is_enabled = True
            logger.info("✅ Google AI Studio berhasil dikonfigurasi")
            
        except ImportError as e:
            logger.error(f"❌ Package google-generativeai tidak terinstall: {e}")
            self.model = None
            self.is_enabled = False
        except Exception as e:
            logger.error(f"❌ Error konfigurasi Google AI: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            self.model = None
            self.is_enabled = False
    
    async def analyze_text(self, text: str, user_id: int) -> str:
        logger.info(f"🧠 AI Analysis requested by user {user_id}")
        
        if not self.is_enabled:
            logger.error("❌ AI Analysis called but AI is not enabled")
            return "Fitur AI tidak tersedia."
        
        try:
            logger.info(f"🧠 Processing text: {text[:50]}...")
            
            prompt = f"""
            Perkenalkan diri Anda sebagai asisten AI Trenbolt-Bot dan berikan respons yang helpful dalam bahasa Indonesia.
            
            Teks pengguna: {text}
            
            Berikan respons yang ramah, informatif, dan helpful dalam bahasa Indonesia.
            """
            
            logger.info("🧠 Sending request to Google AI...")
            
            # Generate content dengan configuration
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            logger.info("✅ AI Response received")
            
            # Handle response
            if response.text:
                return response.text
            else:
                logger.warning("⚠️ AI response is empty")
                return "Maaf, saya tidak mendapatkan respons dari AI. Silakan coba lagi."
            
        except Exception as e:
            logger.error(f"❌ AI Analysis error: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            return f"❌ Error AI: {str(e)}"