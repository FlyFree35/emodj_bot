# -*- coding: utf-8 -*-
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
from telegram import (
    Update, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton, InputFile
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = "https://emodj-bot-1.onrender.com"

keyboard = [
    ["🔍 Поиск по артисту", "🎵 Поиск по названию"],
    ["🎭 Найти по настроению", "⚙️ Настройки"]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def download_mp3_from_youtube(url, cookies_path="youtube_cookies.txt"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiefile': cookies_path,
        'quiet': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        mp3_path = filename.rsplit('.', 1)[0] + '.mp3'
        return mp3_path


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎶 Добро пожаловать в EmoDJ!\nВыбери действие ниже 👇",
        reply_markup=markup
    )


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text == "🔍 поиск по артисту".lower():
        context.user_data["mode"] = "artist"
        await update.message.reply_text("🎤 Введи имя артиста:")
    elif text == "🎵 поиск по названию".lower():
        context.user_data["mode"] = "title"
        await update.message.reply_text("🎶 Введи название песни:")
    elif text == "🎭 найти по настроению".lower():
        context.user_data["mode"] = "mood"
        await update.message.reply_text("🧠 Введи настроение (напр.: весело, грустно):")
    elif text == "⚙️ настройки".lower():
        await update.message.reply_text("⚙️ Пока нет доступных настроек.")
    else:
        await process_query(update, context)


async def process_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    query = update.message.text.strip()

    if mode == "artist":
        search_query = f"{query} official music"
    elif mode == "title":
        search_query = f"{query} official audio"
    elif mode == "mood":
        search_query = f"{query} music playlist"
    else:
        await update.message.reply_text("❗ Сначала выбери действие в меню.")
        return

    search = VideosSearch(search_query, limit=1)
    result = search.result()

    if result['result']:
        video = result['result'][0]
        title = video['title']
        url = video['link']

        context.user_data['last_track'] = {'title': title, 'url': url}

        buttons = [
            [InlineKeyboardButton("🔗 Слушать на YouTube", url=url)],
            [InlineKeyboardButton("⬇️ Скачать MP3", callback_data="download_mp3")]
        ]

        await update.message.reply_text(
            f"🎵 Найдена песня: {title}\nЧто хочешь сделать?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await update.message.reply_text("❌ Ничего не найдено. Попробуй другой запрос.")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download_mp3":
        track = context.user_data.get("last_track")
        if not track:
            await query.edit_message_text("⚠️ Ошибка: трек не найден.")
            return

        title = track["title"]
        url = track["url"]

        await query.edit_message_text(f"⏳ Скачиваю MP3: {title}...")

        try:
            path = download_mp3_from_youtube(url)
            await query.message.reply_audio(audio=InputFile(path), title=title)
            os.remove(path)  # Удаляем после отправки
        except Exception as e:
            print("❌ Ошибка при скачивании:", e)
            await query.message.reply_text("❌ Не удалось скачать MP3. Попробуй другой трек.")


# Запуск приложения
if not os.path.exists("downloads"):
    os.mkdir("downloads")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
app.add_handler(CallbackQueryHandler(handle_callback))

app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 8443)),
    webhook_url=WEBHOOK_URL
)
