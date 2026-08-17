from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from googletrans import Translator

translator = Translator()

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_text = update.message.text
    
    if user_text.startswith('/'):
        return

    try:
        detected = translator.detect(user_text)
        src_lang = detected.lang

        if src_lang == 'ko':
            translation = translator.translate(user_text, dest='vi')
            response_message = f"🇰🇷 ➔ 🇻🇳\n{translation.text}"
        else:
            translation = translator.translate(user_text, dest='ko')
            response_message = f"🇻🇳 ➔ 🇰🇷\n{translation.text}"

    except Exception as e:
        response_message = "Xin lỗi, đã có lỗi xảy ra khi dịch."

    await update.message.reply_text(response_message)

if __name__ == '__main__':
    application = ApplicationBuilder().token("8684404526:AAERMQiQRE5rTTaBeVuqVzdaKSFBqmCiuAc").build()

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_text))

    print("Bot đang chạy...")
    application.run_polling()