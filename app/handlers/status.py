async def test_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test AI dengan prompt sederhana"""
    test_text = "Halo, ini adalah test AI. Bisakah kamu memperkenalkan diri dalam 2-3 kalimat?"
    
    processing_msg = await update.message.reply_text("🧠 Testing AI...")
    
    try:
        from app.services.ai_analyzer import AIAnalyzer
        analyzer = AIAnalyzer()
        
        if not analyzer.is_enabled:
            await processing_msg.delete()
            await update.message.reply_text("❌ AI tidak aktif.")
            return
        
        response = await analyzer.analyze_text(test_text, update.effective_user.id)
        
        await processing_msg.delete()
        
        if response.startswith("❌"):
            result_text = f"""
🧪 **AI Test Result:**

**Status:** ❌ AI Error
**Error:** {response}
"""
        else:
            result_text = f"""
🧪 **AI Test Result:**

**Prompt:** {test_text}

**Response:**
{response}

**Status:** ✅ AI Berfungsi
"""
        await update.message.reply_text(result_text)
        
    except Exception as e:
        await processing_msg.delete()
        await update.message.reply_text(f"❌ AI Test Failed:\n{str(e)}")