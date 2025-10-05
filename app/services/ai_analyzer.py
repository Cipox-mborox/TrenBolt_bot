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
                logger.info(f"📋 Available models: {len(available_models)} models")
                
                # Log beberapa model yang relevan
                gemini_models = [m for m in available_models if 'gemini' in m.lower() and 'flash' in m.lower()]
                if gemini_models:
                    logger.info(f"📋 Gemini Flash models: {gemini_models[:3]}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Cannot list models: {e}")
            
            # Gunakan model yang tersedia dan recommended
            # Berdasarkan list, gunakan models/gemini-2.0-flash atau models/gemini-flash-latest
            preferred_models = [
                'models/gemini-2.0-flash',
                'models/gemini-flash-latest', 
                'models/gemini-2.0-flash-001',
                'models/gemini-2.0-flash-lite',
                'models/gemini-pro-latest'
            ]
            
            model_name = None
            for model in preferred_models:
                try:
                    self.model = genai.GenerativeModel(model)
                    # Test dengan prompt sederhana
                    test_response = self.model.generate_content("Test")
                    model_name = model
                    logger.info(f"✅ Successfully using model: {model}")
                    break
                except Exception as e:
                    logger.warning(f"❌ Model {model} failed: {e}")
                    continue
            
            if not model_name:
                # Fallback: coba model apa saja yang ada 'flash'
                flash_models = [m for m in available_models if 'flash' in m.lower()]
                for model in flash_models[:3]:  # Coba 3 model flash pertama
                    try:
                        self.model = genai.GenerativeModel(model)
                        model_name = model
                        logger.info(f"✅ Fallback to model: {model}")
                        break
                    except Exception as e:
                        logger.warning(f"❌ Fallback model {model} failed: {e}")
                        continue
            
            if not model_name:
                logger.error("❌ No working model found")
                self.model = None
                self.is_enabled = False
                return
            
            self.model_name = model_name
            self.is_enabled = True
            logger.info(f"✅ Google AI Studio berhasil dikonfigurasi dengan model: {model_name}")
            
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
            logger.info(f"🧠 Processing text with model {self.model_name}: {text[:50]}...")
            
            prompt = f"""
            Anda adalah asisten AI yang helpful. Berikan respons dalam bahasa Indonesia.
            
            Pertanyaan: {text}
            
            Berikan respons yang informatif, ramah, dan helpful dalam bahasa Indonesia.
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