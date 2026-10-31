import os
import telebot
from google import genai

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

print("--- KONTROL PANELİ ---")
print("Telegram Token:", "✅ Yüklendi" if TELEGRAM_TOKEN else "❌ EKSİK!")
print("Gemini API Key:", "✅ Yüklendi" if GEMINI_KEY else "❌ EKSİK!")
print("----------------------")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_KEY)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Merhaba kanka! Ben Gemini yapay zeka destekli asistanınım.")

@bot.message_handler(func=lambda message: True)
def handle_ai_response(message):
    print(f"📩 Mesaj geldi: '{message.text}'")
    try:
        # Kota harcamayan, en sade ve ultra hızlı AI üretimi
        response = ai_client.models.generate_content(
            model='gemini-3.8-flash',
            contents=message.text
        )
        print("🤖 Gemini Yanıt Üretti!")
        bot.reply_to(message, response.text)
    except Exception as e:
        print("💥 GEMINI HATASI:", e)
        if "429" in str(e):
            bot.reply_to(message, "Kanka çok hızlı mesaj attık, Google 1 dakikalık mola verdi. Birazdan tekrar yaz!")
        else:
            bot.reply_to(message, f"Ufak bir sorun oluştu kanka: {e}")

if __name__ == "__main__":
    print("Bot çalışıyor, mesaj bekleniyor...")
    bot.infinity_polling()