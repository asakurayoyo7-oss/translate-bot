import os
import threading
import requests
import json
from flask import Flask, request
import telebot

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# Hàm gọi Gemini trực tiếp qua REST API của Google Cloud (hỗ trợ key AQ...)
def translate_with_gemini(text):
    # Xác định hướng dịch để đưa prompt tối ưu
    has_korean = any(ord('가') <= ord(c) <= ord('힣') for c in text)
    if has_korean:
        prompt = f"Dịch câu sau sang tiếng Việt tự nhiên, giữ nguyên ý nghĩa, tuyệt đối không thêm từ xưng hô: {text}"
        direction_label = "🇰🇷 ➔ 🇻🇳"
    else:
        prompt = f"Dịch câu sau sang tiếng Hàn, dùng văn phong kính ngữ lịch sự (존댓말), chỉ trả về kết quả không kèm giải thích: {text}"
        direction_label = "🇻🇳 ➔ 🇰🇷"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        
        if "candidates" in res_json:
            translated_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            return f"{direction_label}\n{translated_text}"
        else:
            print(f"Lỗi trả về từ Google API: {res_json}")
            return f"Lỗi API: {res_json.get('error', {}).get('message', 'Không rõ nguyên nhân')}"
    except Exception as e:
        print(f"Lỗi kết nối API: {e}")
        return f"Lỗi kết nối: {str(e)}"

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
def handle_message(message):
    text = message.text
    if not text or text.startswith('/'):
        return

    # Gọi hàm dịch trực tiếp và phản hồi lại Telegram
    result = translate_with_gemini(text)
    bot.reply_to(message, result)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
