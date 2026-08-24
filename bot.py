import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Đảm bảo kết quả nhận diện ngôn ngữ ổn định
DetectorFactory.seed = 0

# --- PHẦN 1: MÁY CHỦ WEB GIẢ LẬP CHO RENDER ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# --- PHẦN 2: LOGGING VÀ LOGIC DỊCH TỰ ĐỘNG THÔNG MINH ---
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
        # Tự động phát hiện ngôn ngữ của tin nhắn
        detected_lang = detect(user_text)
        
        # Nếu ngôn ngữ phát hiện là Tiếng Việt ('vi') -> Dịch sang Tiếng Hàn
        if detected_lang == 'vi':
            translated = GoogleTranslator(source='vi', target='ko').translate(user_text)
            header = "🇻🇳 → 🇰🇷"
        else:
            # Ngược lại (Tiếng Hàn, Tiếng Anh,...) -> Dịch sang Tiếng Việt
            translated = GoogleTranslator(source='auto', target='vi').translate(user_text)
            header = "🇰🇷 → 🇻🇳"

        if translated:
            final_reply = f"{header}\n{translated}"
            await update.message.reply_text(final_reply)
            
    except Exception as e:
        print(f"Lỗi dịch thuật: {e}")

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    print("Web server giả lập đã khởi động...")

    TOKEN = '8640156640:AAGEFPqRwrVoEj38gfPoiFrrvHwhGtcrJTE'
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))
    
    print("Bot dịch tự động đang chạy...")
    app.run_polling()
