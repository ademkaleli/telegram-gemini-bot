import os
import sys
import time
import traceback
from flask import Flask, request
import telebot
from google import genai

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
ai_client = genai.Client(api_key=GEMINI_KEY)

app = Flask(__name__)

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    except Exception as e:
        print(f"Webhook hatası: {e}", file=sys.stderr, flush=True)
        return "Error", 500

@app.route('/')
def webhook():
    bot.remove_webhook()
    success = bot.set_webhook(url='https://wezoxy.pythonanywhere.com/' + TELEGRAM_TOKEN)
    if success:
        return "✅ Telegram Webhook Başarıyla Kuruldu!", 200
    return "❌ Hata", 500

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Merhaba kanka! Ben Gemini yapay zeka destekli asistanınım.")

@bot.message_handler(func=lambda message: True)
def handle_ai_response(message):
    # Google 503 yoğunluk hatası verirse 3 kere otomatik tekrar dener
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = ai_client.models.generate_content(
                model='gemini-3.8-flash',
                contents=message.text
            )
            bot.reply_to(message, response.text)
            return
        except Exception as e:
            err_msg = str(e)
            if ("503" in err_msg or "UNAVAILABLE" in err_msg) and attempt < max_retries - 1:
                time.sleep(1)  # 1 saniye bekleyip tekrar dene
                continue
            
            print(f"Gemini Hatası: {e}", flush=True)
            bot.reply_to(message, "Google sunucularında anlık yoğunluk var kanka, lütfen birkaç saniye sonra tekrar yaz!")
            break
