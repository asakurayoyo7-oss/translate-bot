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
    
    # Bỏ qua nếu tin nhắn là lệnh (bắt đầu bằng /)
    if user_text.startswith('/'):
        return

    try:
        # Kiểm tra xem có ký tự tiếng Hàn (Hangul) trong câu không
        has_korean = any('가' <= c <= '힣' for c in user_text)
        
        if has_korean:
            # Nếu có tiếng Hàn -> Dịch sang Tiếng Việt
            translated = GoogleTranslator(source='ko', target='vi').translate(user_text)
            # Tiêu đề: Cờ Hàn -> Mũi tên nhỏ -> Cờ Việt
            header = "🇰🇷 → 🇻🇳"
        else:
            # Nếu là tiếng Việt -> Dịch sang Tiếng Hàn kính ngữ/trang trọng
            translated = GoogleTranslator(source='vi', target='ko').translate(user_text)
            # Tiêu đề: Cờ Việt -> Mũi tên nhỏ -> Cờ Hàn
            header = "🇻🇳 → 🇰🇷"

        # Trả về kết quả với tiêu đề gọn gàng ở trên
        if translated:
            final_reply = f"{header}\n{translated}"
            await update.message.reply_text(final_reply)
            
    except Exception as e:
        # Ghi log lỗi nếu có (không in ra chat để tránh rối)
        print(f"Lỗi dịch thuật: {e}")

if __name__ == '__main__':
    # Token của bạn
    TOKEN = '8640156640:AAGEFPqRwrVoEj38gfPoiFrrvHwhGtcrJTE'
    
    # Khởi tạo ứng dụng
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Thêm bộ xử lý tin nhắn văn bản
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))
    
    print("Bot dịch Hàn - Việt đang chạy...")
    # Chạy bot
    app.run_polling()
