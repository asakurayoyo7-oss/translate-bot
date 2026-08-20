import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from deep_translator import GoogleTranslator

# Thiết lập ghi log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_text = update.message.text.strip()
    
    if user_text.startswith('/'):
        return

    try:
        # Kiểm tra xem có ký tự tiếng Hàn (Hangul) trong câu không
        has_korean = any('가' <= c <= '힣' for c in user_text)
        
        if has_korean:
            # Nếu là tiếng Hàn -> Dịch sang Tiếng Việt
            translated = GoogleTranslator(source='ko', target='vi').translate(user_text)
            # Cờ cho chiều Hàn -> Việt (Hiển thị trên một dòng riêng)
            flag_line = "🇰🇷 ➡️ 🇻🇳"
        else:
            # Nếu là tiếng Việt -> Dịch sang Tiếng Hàn
            translated = GoogleTranslator(source='vi', target='ko').translate(user_text)
            # Cờ cho chiều Việt -> Hàn (Hiển thị trên một dòng riêng)
            flag_line = "🇻🇳 ➡️ 🇰🇷"

        # Trả về kết quả: Dòng cờ, xuống dòng (\n), sau đó là nội dung dịch
        if translated:
            final_reply = f"{flag_line}\n{translated}"
            await update.message.reply_text(final_reply)
            
    except Exception as e:
        print(f"Lỗi dịch thuật: {e}")

if __name__ == '__main__':
    # Token của bạn
    TOKEN = '8640156640:AAGEFPqRwrVoEj38gfPoiFrrvHwhGtcrJTE'
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))
    
    print("Bot dịch Hàn - Việt đang chạy...")
    app.run_polling()
