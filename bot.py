import os
from flask import Flask, request
import telebot
from google import genai

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_KEY)

app = Flask(__name__)

# Telegram'dan gelecek mesajları karşılayan Webhook adresi
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# Webhook bağlantısını kuran ana sayfa
@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://wezoxy.pythonanywhere.com/' + TELEGRAM_TOKEN)
    return "✅ Telegram Webhook Bağlantısı Başarıyla Kuruldu!", 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Merhaba kanka! Ben Gemini yapay zeka destekli asistanınım.")

@bot.message_handler(func=lambda message: True)
def handle_ai_response(message):
    try:
        response = ai_client.models.generate_content(
            model='gemini-3.8-flash',
            contents=message.text
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Hata oluştu kanka: {e}")
