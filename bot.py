import os
import telebot
from google import genai
from google.genai import types

# Lấy token từ biến môi trường trên Render
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

@bot.message_handler(func=lambda message: True)
def translate_message(message):
    text = message.text
    if not text:
        return

    try:
        # Prompt hệ thống ép buộc AI dịch chuẩn kính ngữ tiếng Hàn
        system_instruction = (
            "Bạn là một biên phiên dịch chuyên nghiệp. Hãy dịch câu được cung cấp: "
            "Nếu là tiếng Việt, hãy dịch sang tiếng Hàn. Nếu là tiếng Hàn, hãy dịch sang tiếng Việt. "
            "QUY TẮC BẮT BUỘC KHI DỊCH SANG TIẾNG HÀN: "
            "Phải luôn dùng văn phong kính ngữ lịch sự, trang trọng (존댓말 - sử dụng đuôi câu kính ngữ như -아요/어요, -ㅂ니다/습니다, v.v.), "
            "tuyệt đối không dùng thể trống không hay thân mật (반말). "
            "Chỉ trả về kết quả dịch, không kèm theo bất kỳ giải thích hay lời dẫn nào khác."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            ),
        )
        
        translated_text = response.text.strip()

        # Xác định chiều dịch để hiển thị icon cho đẹp
        # Kiểm tra xem text gốc có chứa ký tự tiếng Hàn hay không
        has_korean = any(ord('가') <= ord(c) <= ord('힣') for c in text)
        
        if has_korean:
            direction_label = "🇰🇷 ➔ 🇻🇳"
        else:
            direction_label = "🇻🇳 ➔ 🇰🇷"

        # Gửi kết quả dịch lại vào nhóm
        reply_text = f"{direction_label}\n{translated_text}"
        bot.reply_to(message, reply_text)

    except Exception as e:
        print(f"Lỗi dịch: {e}")

if __name__ == "__main__":
    print("Bot đang chạy...")
    bot.infinity_polling()
