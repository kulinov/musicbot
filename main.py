import telebot
from yt_dlp import YoutubeDL
import os
from pydub import AudioSegment
import logging
from flask import Flask
from threading import Thread

# Логирование
logging.basicConfig(level=logging.DEBUG, filename='bot_errors.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Токен вашего Telegram-бота
BOT_TOKEN = '8040295705:AAEwkOPQnuiwVqZ_B-iCgRwQY9mP09clHJ0'

bot = telebot.TeleBot(BOT_TOKEN)

# Создаем Flask приложение
app = Flask(__name__)

@app.route('/')
def index():
    return "Telegram bot работает!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Напиши название песни, и я найду её для тебя 🎵")

@bot.message_handler(func=lambda message: True)
def search_and_send_music(message):
    query = message.text
    bot.reply_to(message, f"Ищу песню: {query}... Подождите немного 🎧")

    try:
        # Параметры для загрузки аудио
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
        }

        # Поиск и загрузка аудио
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            file_name = ydl.prepare_filename(info)

        # Проверка существования файла
        if not os.path.exists(file_name):
            bot.reply_to(message, "Ошибка: файл с песней не найден 😔.")
            logging.error(f"Файл не найден после загрузки: {file_name}")
            return

        # Преобразование в MP3, если требуется
        if not file_name.endswith('.mp3'):
            mp3_file = os.path.splitext(file_name)[0] + '.mp3'
            AudioSegment.from_file(file_name).export(mp3_file, format='mp3')
            os.remove(file_name)  # Удаляем оригинал
            file_name = mp3_file

        # Проверка размера файла
        file_size = os.path.getsize(file_name)
        if file_size > 50 * 1024 * 1024:  # 50 МБ
            bot.reply_to(message, "Файл слишком большой для отправки 😔. Попробуйте найти другую песню.")
            os.remove(file_name)
            return

        # Отправка аудио в чат
        with open(file_name, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info['title'], performer=info.get('uploader', 'Unknown'))

        # Удаление файла после отправки
        os.remove(file_name)

    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        bot.reply_to(message, f"Не удалось найти или загрузить песню 😔\nОшибка: {e}")

# Функция для запуска Flask в отдельном потоке
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Запуск Flask в отдельном потоке
flask_thread = Thread(target=run_flask)
flask_thread.start()

# Запуск бота
bot.polling()
