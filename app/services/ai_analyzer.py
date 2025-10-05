import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
        
        logger.info(f"🔧 Initializing AI Analyzer...")
        logger.info(f"🔧 API Key available: {bool(api_key)}")
        logger.info(f"🔧 API Key length: {len(api_key) if api_key else 0}")
        
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
            
            # Test model availability
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("✅ GenerativeModel created")
            
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
            Analisis teks berikut dan berikan insights yang berguna dalam bahasa Indonesia:
            
            "{text}"
            
            Format respons:
            1. **Ringkasan** - Ringkasan singkat tentang teks
            2. **Poin Penting** - Beberapa poin penting yang ditemukan
            3. **Insights** - Wawasan atau analisis mendalam
            4. **Rekomendasi** - Saran tindakan selanjutnya (jika applicable)
            
            Gunakan bahasa Indonesia yang natural dan mudah dipahami.
            """
            
            logger.info("🧠 Sending request to Google AI...")
            response = self.model.generate_content(prompt)
            logger.info("✅ AI Response received")
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ AI Analysis error: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            return f"❌ Maaf, terjadi error saat menganalisis dengan AI: {str(e)}"