import os
import threading
from flask import Flask
import telebot
import google.generativeai as genai

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

genai.configure(api_key=GEMINI_API_KEY)

system_instruction = (
    "Bạn là một biên phiên dịch chuyên nghiệp. Hãy dịch câu được cung cấp: "
    "Nếu là tiếng Việt, hãy dịch sang tiếng Hàn. Nếu là tiếng Hàn, hãy dịch sang tiếng Việt. "
    "QUY TẮC BẮT BUỘC: "
    "1. Khi dịch sang tiếng Hàn, phải dùng văn phong kính ngữ lịch sự (존댓말). "
    "2. Khi dịch sang tiếng Việt, phải giữ đúng ý nghĩa gốc, tuyệt đối không tự ý thêm từ xưng hô. "
    "3. Chỉ trả về kết quả dịch, không kèm giải thích."
)

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=system_instruction
)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def translate_message(message):
    text = message.text
    if not text or text.startswith('/'):
        return

    try:
        response = model.generate_content(text)
        translated_text = response.text.strip()
        
        has_korean = any(ord('가') <= ord(c) <= ord('힣') for c in text)
        direction_label = "🇰🇷 ➔ 🇻🇳" if has_korean else "🇻🇳 ➔ 🇰🇷"

        reply_text = f"{direction_label}\n{translated_text}"
        bot.reply_to(message, reply_text)
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()
    
    # Xóa webhook cũ đang bị treo để tránh lỗi 409 Conflict
    bot.remove_webhook()
    
    print("Bot đã khởi động thành công và sẵn sàng dịch...")
    bot.infinity_polling(skip_pending=True)
