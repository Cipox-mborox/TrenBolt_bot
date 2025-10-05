# Trenbolt-Bot 🤖

Bot Telegram AI yang powerful untuk analisis tren dan konten, dibangun dengan Google AI Studio dan deployed di Railway.

## Fitur ✨

- ✅ Analisis teks dengan AI
- ✅ Transkripsi audio ke teks
- ✅ Sistem premium
- ✅ Database PostgreSQL
- ✅ Rate limiting

## Tech Stack 🛠️

- Python 3.9+
- python-telegram-bot
- Google Generative AI
- PostgreSQL
- Railway (Deployment)

## Setup 🔧

1. Clone repository
2. Copy `.env.example` ke `.env`
3. Isi environment variables:
   - `TELEGRAM_BOT_TOKEN` dari @BotFather
   - `GOOGLE_AI_STUDIO_API_KEY` dari Google AI Studio
   - `DATABASE_URL` dari Railway PostgreSQL

4. Install dependencies:
```bash
pip install -r requirements.txt