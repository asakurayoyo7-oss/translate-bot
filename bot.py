import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from deep_translator import GoogleTranslator

# --- PHẦN 1: TẠO MÁY CHỦ WEB GIẢ LẬP CHO RENDER & UPTIMEROBOT ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# --- PHẦN 2: LOGGING VÀ LOGIC BOT TELEGRAM ---
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
        has_korean = any('가' <= c <= '힣' for c in user_text)
        
        if has_korean:
            translated = GoogleTranslator(source='ko', target='vi').translate(user_text)
            header = "🇰🇷 → 🇻🇳"
        else:
            translated = GoogleTranslator(source='vi', target='ko').translate(user_text)
            header = "🇻🇳 → 🇰🇷"

        if translated:
            final_reply = f"{header}\n{translated}"
            await update.message.reply_text(final_reply)
            
    except Exception as e:
        print(f"Lỗi dịch thuật: {e}")

if __name__ == '__main__':
    # Khởi chạy web server ở một luồng riêng để Render và UptimeRobot nhận diện
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    print("Web server giả lập đã khởi động...")

    # Token của bot
    TOKEN = '8640156640:AAGEFPqRwrVoEj38gfPoiFrrvHwhGtcrJTE'
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))
    
    print("Bot dịch Hàn - Việt đang chạy...")
    app.run_polling()
