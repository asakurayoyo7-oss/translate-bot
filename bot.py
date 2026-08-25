import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from deep_translator import GoogleTranslator

# --- CẤU HÌNH LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- HÀM XỬ LÝ DỊCH THUẬT 2 CHIỀU (HÀN <-> VIỆT) ---
async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_text = update.message.text.strip()
    
    if user_text.startswith('/'):
        return

    try:
        # Kiểm tra xem trong câu có chứa ký tự tiếng Hàn (Hangul) hay không
        korean_char_count = sum(1 for c in user_text if '가' <= c <= '힣')
        
        if korean_char_count > 0:
            # Nếu có chữ Hàn -> Dịch sang Tiếng Việt
            translated = GoogleTranslator(source='ko', target='vi').translate(user_text)
            header = "🇰🇷 → 🇻🇳"
        else:
            # Ngược lại (Tiếng Việt hoặc ngôn ngữ khác) -> Dịch sang Tiếng Hàn
            translated = GoogleTranslator(source='vi', target='ko').translate(user_text)
            header = "🇻🇳 → 🇰🇷"

        if translated:
            final_reply = f"{header}\n{translated}"
            await update.message.reply_text(final_reply)
            
    except Exception as e:
        print(f"Lỗi dịch thuật: {e}")

# --- MÁY CHỦ HTTP ĐỂ ĐÁP ỨNG RENDER WEB SERVICE ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")
    def log_message(self, format, *args):
        return # Tắt log thừa để tiết kiệm bộ nhớ

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

if __name__ == '__main__':
    # Khởi động web server bằng phương thức đơn giản
    import multiprocessing
    server_process = multiprocessing.Process(target=run_web_server)
    server_process.daemon = True
    server_process.start()
    print("Web server đã khởi động...")

    # Token của bot Telegram
    TOKEN = '8640156640:AAGEFPqRwrVoEj38gfPoiFrrvHwhGtcrJTE'
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))
    
    print("Bot đang chạy vòng lặp nhận tin nhắn...")
    app.run_polling(drop_pending_updates=True)
