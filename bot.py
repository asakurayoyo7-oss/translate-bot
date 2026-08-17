import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from deep_translator import GoogleTranslator

# Web server giả lập để Render duy trì cổng hoạt động 24/7
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Hàm tự động thêm văn phong kính ngữ/trang trọng khi dịch sang tiếng Việt
def apply_honorifics(text):
    if not text.startswith("Dạ, "):
        text = "Dạ, " + text[0].lower() + text[1:]
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
            translation = GoogleTranslator(source='ko', target='vi').translate(user_text)
            polite_text = apply_honorifics(translation)
            response_message = f"🇰🇷 ➔ 🇻🇳 (Kính ngữ)\n{polite_text}"
        else:
            translation = GoogleTranslator(source='vi', target='ko').translate(user_text)
            response_message = f"🇻🇳 ➔ 🇰🇷\n{translation}"
            
        await update.message.reply_text(response_message)
        
    except Exception:
        try:
            if is_korean:
                fallback_trans = GoogleTranslator(source='ko', target='vi').translate(user_text)
                await update.message.reply_text(f"🇰🇷 ➔ 🇻🇳 (Kính ngữ)\n{apply_honorifics(fallback_trans)}")
            else:
                fallback_trans = GoogleTranslator(source='vi', target='ko').translate(user_text)
                await update.message.reply_text(f"🇻🇳 ➔ 🇰🇷\n{fallback_trans}")
        except Exception:
            pass

async def main():
    # Khởi chạy Web Server ở luồng riêng
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Khởi chạy Telegram Bot ứng dụng phiên bản mới
    application = ApplicationBuilder().token("8684404526:AAERMQiQRE5rTTaBeVuqVzdaKSFBqmCiuAc").build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Giữ cho bot chạy liên tục
    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == '__main__':
    asyncio.run(main())
