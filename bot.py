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
            # Nếu có tiếng Hàn -> Dịch sang Tiếng Việt
            translated = GoogleTranslator(source='ko', target='vi').translate(user_text)
        else:
            # Nếu là tiếng Việt (hoặc ngôn ngữ khác) -> Dịch sang Tiếng Hàn kính ngữ/trang trọng
            translated = GoogleTranslator(source='vi', target='ko').translate(user_text)

        # Trả về kết quả dịch chuẩn xác
        if translated:
            await update.message.reply_text(translated)
            
    except Exception as e:
        print(f"Lỗi dịch thuật: {e}")
        # Không làm gì thêm để tránh spam lỗi vào nhóm

if __name__ == '__main__':
    # Token của bạn
    TOKEN = '8640156640:AAGEFPqRwrVoEj38gfPoiFrrvHwhGtcrJTE'
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))
    
    print("Bot dịch Hàn - Việt đang chạy...")
    app.run_polling()
