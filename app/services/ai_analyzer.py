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
                logger.info(f"📋 Total available models: {len(available_models)}")
                
                # Filter hanya model yang support generateContent
                supported_models = []
                for model_name in available_models:
                    for model in models:
                        if model.name == model_name and 'generateContent' in model.supported_generation_methods:
                            supported_models.append(model_name)
                            break
                
                logger.info(f"📋 Models supporting generateContent: {len(supported_models)}")
                
                # Log beberapa model yang supported
                if supported_models:
                    logger.info(f"📋 Supported models sample: {supported_models[:5]}")
                
            except Exception as e:
                logger.warning(f"⚠️ Cannot list models: {e}")
                supported_models = []
            
            # Gunakan model yang tersedia dan supported untuk generateContent
            # Berdasarkan list Anda, gunakan model yang ada di supported_models
            preferred_models = [
                'models/gemini-2.0-flash',
                'models/gemini-flash-latest', 
                'models/gemini-2.0-flash-001',
                'models/gemini-2.0-flash-lite',
                'models/gemini-pro-latest',
                'models/gemini-2.5-flash',
                'models/gemini-2.0-flash-exp'
            ]
            
            model_name = None
            for model in preferred_models:
                if model in supported_models:
                    try:
                        self.model = genai.GenerativeModel(model)
                        # Test cepat dengan prompt sederhana
                        test_response = self.model.generate_content("Test", request_options={"timeout": 10})
                        if test_response.text:
                            model_name = model
                            logger.info(f"✅ Successfully using model: {model}")
                            break
                        else:
                            logger.warning(f"⚠️ Model {model} returned empty response")
                    except Exception as e:
                        logger.warning(f"❌ Model {model} failed: {e}")
                        continue
            
            # Jika preferred models tidak bekerja, coba model supported lainnya
            if not model_name and supported_models:
                for model in supported_models[:5]:  # Coba 5 model supported pertama
                    if any(flash in model for flash in ['flash', 'gemini']):  # Prioritize flash/gemini models
                        try:
                            self.model = genai.GenerativeModel(model)
                            test_response = self.model.generate_content("Test", request_options={"timeout": 10})
                            if test_response.text:
                                model_name = model
                                logger.info(f"✅ Fallback to supported model: {model}")
                                break
                        except Exception as e:
                            logger.warning(f"❌ Supported model {model} failed: {e}")
                            continue
            
            if not model_name:
                logger.error("❌ No working model found from supported models")
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
                generation_config=generation_config,
                request_options={"timeout": 30}  # Timeout 30 detik
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