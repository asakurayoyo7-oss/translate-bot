import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from aiohttp import web
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
        korean_char_count = sum(1 for c in user_text if '가' <= c <= '힣')
        
        if korean_char_count > 0:
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

# --- WEB SERVER ĐỂ GIỮ RENDER KHÔNG NGỦ ĐÔNG ---
async def health_check(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app_web = web.Application()
    app_web.router.add_get("/", health_check)
    runner = web.AppRunner(app_web)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    # Khởi động web server ngầm bằng async để không xung đột với bot
    await start_web_server()

    # Token của bot Telegram
    TOKEN = '8640156640:AAGPxlCnFra379danxa-SPD0K59W1zZ-Te8'
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))
    
    print("Bot đang chạy...")
    # drop_pending_updates=True giúp xóa các tin nhắn cũ bị kẹt, tránh xung đột Conflict
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    # Giữ ứng dụng luôn chạy
    import asyncio
    await asyncio.Event().wait()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
