import os
import threading
from flask import Flask, request
import telebot
import google.generativeai as genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

system_instruction = (
    "Bạn là một biên phiên dịch chuyên nghiệp. Hãy dịch câu được cung cấp: "
    "Nếu là tiếng Việt, hãy dịch sang tiếng Hàn. Nếu là tiếng Hàn, hãy dịch sang tiếng Việt. "
    "QUY TẮC BẮT BUỘC: "
    "1. Khi dịch sang tiếng Hàn, phải dùng văn phong kính ngữ lịch sự (존댓말). "
    "2. Khi dịch sang tiếng Việt, phải giữ đúng ý nghĩa gốc, tuyệt đối không tự ý thêm từ xưng hô. "
    "3. Chỉ trả về kết quả dịch, không kèm giải thích."
)

# Đổi sang model chuẩn tương thích với Vertex AI key
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash-002',
    system_instruction=system_instruction
)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    except Exception as e:
        print(f"Lỗi Webhook: {e}")
    return "OK", 200

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
        print(f"Lỗi AI: {e}")
        bot.reply_to(message, f"Lỗi AI: {str(e)}")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
