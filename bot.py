import os
import threading
from flask import Flask
import telebot
from google import genai
from google.genai import types

# --- Phần tạo Web Server nhỏ để bot không bị ngủ đông ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
# --------------------------------------------------------

# Lấy thông tin an toàn từ biến môi trường trên Render
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Khởi tạo bot và client
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

@bot.message_handler(func=lambda message: True)
def translate_message(message):
    text = message.text
    if not text:
        return

    try:
        system_instruction = (
            "Bạn là một biên phiên dịch chuyên nghiệp. Hãy dịch câu được cung cấp: "
            "Nếu là tiếng Việt, hãy dịch sang tiếng Hàn. Nếu là tiếng Hàn, hãy dịch sang tiếng Việt. "
            "QUY TẮC BẮT BUỘC: "
            "1. Khi dịch sang tiếng Hàn, phải dùng văn phong kính ngữ lịch sự (존댓말), không dùng thể trống không. "
            "2. Khi dịch sang tiếng Việt, phải giữ đúng ý nghĩa gốc, tuyệt đối không tự ý thêm các từ xưng hô như 'sếp', 'đại diện' hay thay đổi chủ ngữ nếu câu gốc không có. "
            "3. Chỉ trả về kết quả dịch, không kèm theo bất kỳ giải thích nào."
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            ),
        )
        
        translated_text = response.text.strip()
        has_korean = any(ord('가') <= ord(c) <= ord('힣') for c in text)
        
        if has_korean:
            direction_label = "🇰🇷 ➔ 🇻🇳"
        else:
            direction_label = "🇻🇳 ➔ 🇰🇷"

        reply_text = f"{direction_label}\n{translated_text}"
        bot.reply_to(message, reply_text)

    except Exception as e:
        print(f"Lỗi dịch: {e}")

if __name__ == "__main__":
    # Chạy Web Server trong một luồng riêng
    t = threading.Thread(target=run_web)
    t.start()
    
    print("Bot và Web Server đang chạy...")
    bot.infinity_polling()
