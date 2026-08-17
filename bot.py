import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from deep_translator import GoogleTranslator

# Tạo một web server giả lập để Render nhận diện cổng (port)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text

    if user_text.startswith('/'):
        return

    try:
        # Tự động nhận diện tiếng Hàn để dịch sang Việt, hoặc ngược lại
        if any('\uac00' <= char <= '\ud7a3' for char in user_text):
            translation = GoogleTranslator(source='ko', target='vi').translate(user_text)
            response_message = f"🇰🇷 ➔ 🇻🇳\n{translation}"
        else:
            translation = GoogleTranslator(source='vi', target='ko').translate(user_text)
            response_message = f"🇻🇳 ➔ 🇰🇷\n{translation}"
            
    except Exception as e:
        response_message = "Xin lỗi, đã có lỗi xảy ra khi dịch."

    await update.message.reply_text(response_message)

if __name__ == '__main__':
    # Chạy web server giả lập ở một luồng riêng biệt (background thread)
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

    # Chạy Telegram Bot
    application = ApplicationBuilder().token("8684404526:AAERMQiQRE5rTTaBeVuqVzdaKSFBqmCiuAc").build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))
    application.run_polling()
