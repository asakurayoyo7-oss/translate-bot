import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from googletrans import Translator

translator = Translator()

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Hàm xử lý văn phong lịch sự khi dịch sang tiếng Việt
def apply_honorifics(text):
    # Thêm sự trang trọng vào đầu câu nếu chưa có
    if not text.startswith("Dạ, "):
        text = "Dạ, " + text[0].lower() + text[1:]
    # Thay thế các từ xưng hô thông thường thành trang trọng hơn
    text = text.replace("Bạn", "Sếp").replace("bạn", "sếp")
    return text

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    if user_text.startswith('/'):
        return

    try:
        is_korean = any('\uac00' <= char <= '\ud7a3' for char in user_text)
        
        if is_korean:
            # Dịch từ Hàn sang Việt và ép thêm kính ngữ
            translation = translator.translate(user_text, src='ko', dest='vi')
            polite_text = apply_honorifics(translation.text)
            response_message = f"🇰🇷 ➔ 🇻🇳 (Kính ngữ)\n{polite_text}"
        else:
            # Dịch từ Việt sang Hàn (thường tiếng Hàn dùng thể lịch sự/đuôi câu -습니다/입니다)
            translation = translator.translate(user_text, src='vi', dest='ko')
            response_message = f"🇻🇳 ➔ 🇰🇷\n{translation.text}"
            
        await update.message.reply_text(response_message)
        
    except Exception:
        pass

if __name__ == '__main__':
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

    application = ApplicationBuilder().token("8684404526:AAERMQiQRE5rTTaBeVuqVzdaKSFBqmCiuAc").build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))
    application.run_polling()
