import os
import google.generativeai as genai
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_AI_STUDIO_API_KEY tidak ditemukan!")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def analyze_text(self, text: str, user_id: int) -> str:
        try:
            prompt = f"""
            Analisis teks berikut dan berikan insights yang berguna:
            
            "{text}"
            
            Berikan analisis dalam format:
            1. Ringkasan singkat
            2. Poin-poin penting
            3. Rekomendasi tindakan (jika applicable)
            
            Gunakan bahasa Indonesia yang mudah dipahami.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"AI Analysis error: {e}")
            return "Maaf, saya mengalami kesalahan dalam menganalisis teks ini. Silakan coba lagi dengan teks yang berbeda."
    
    async def generate_content_ideas(self, topic: str, user_id: int) -> list:
        try:
            prompt = f"""
            Generate 5 content ideas tentang: {topic}
            
            Format setiap ide:
            - Judul menarik
            - Target audience
            - Platform yang cocok
            - Poin-poin konten
            
            Dalam bahasa Indonesia.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.split('\n\n')
            
        except Exception as e:
            logger.error(f"Content generation error: {e}")
            return ["Maaf, tidak dapat menghasilkan ide konten saat ini."]