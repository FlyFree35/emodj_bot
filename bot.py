# -*- coding: utf-8 -*-
import os
import sys
import io

# Защита от UnicodeEncodeError при работе с эмодзи
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
from telegram import (
    Update, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from youtubesearchpython import VideosSearch

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = "https://emodj-bot-1.onrender.com"

keyboard = [
    ["🔍 Поиск по артисту", "🎵 Поиск по названию"],
    ["🎭 Найти по настроению", "⚙️ Настройки"]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

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

# ВРЕМЕННАЯ ЗАГЛУШКА для кнопки "Скачать MP3"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download_mp3":
        track = context.user_data.get("last_track")
        if not track:
            await query.edit_message_text("⚠️ Ошибка: трек не найден.")
            return

        title = track["title"]

        await query.edit_message_text(
            f"🎵 Трек: *{title}*\n\n"
            "🔧 Функция скачивания MP3 скоро будет доступна!\n"
            "Следи за обновлениями EmoDJ 🎧",
            parse_mode="Markdown"
        )

# Запуск приложения
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
app.add_handler(CallbackQueryHandler(handle_callback))

app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 8443)),
    webhook_url=WEBHOOK_URL
)

