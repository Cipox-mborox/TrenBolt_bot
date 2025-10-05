import os
import logging
import google.generativeai as genai

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
            # Configure API
            genai.configure(api_key=api_key)
            logger.info("✅ Google AI configured")
            
            # Langsung gunakan model yang kita tahu berhasil
            self.model = genai.GenerativeModel('models/gemini-2.0-flash')
            self.is_enabled = True
            logger.info("✅ AI Analyzer initialized with models/gemini-2.0-flash")
            
        except Exception as e:
            logger.error(f"❌ Error initializing AI: {e}")
            self.model = None
            self.is_enabled = False
    
    async def analyze_text(self, text: str, user_id: int) -> str:
        logger.info(f"🧠 AI Analysis requested by user {user_id}")
        
        if not self.is_enabled:
            return "❌ Fitur AI sedang tidak tersedia."
        
        try:
            logger.info(f"🧠 Processing: {text[:50]}...")
            
            # Prompt yang lebih sederhana dengan batasan panjang
            prompt = f"""
            Anda adalah asisten AI yang helpful. Berikan respons dalam bahasa Indonesia.
            Berikan respons yang singkat, padat, dan jelas (maksimal 500 kata).
            
            Pertanyaan/pesan: {text}
            
            Berikan respons yang ramah, informatif, dan helpful dalam bahasa Indonesia.
            """
            
            # Generate response dengan batasan token
            generation_config = {
                "max_output_tokens": 800,  # Batasi output
                "temperature": 0.7,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            logger.info("✅ AI Response received successfully")
            
            return response.text if response.text else "❌ Tidak ada respons dari AI."
            
        except Exception as e:
            logger.error(f"❌ AI Analysis error: {e}")
            return f"❌ Error AI: {str(e)}"