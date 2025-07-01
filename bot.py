import os
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
from pytube import YouTube
import uuid  # Для уникальных имен файлов

# Токен и URL (укажи свои)
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = "https://emodj-bot-1.onrender.com"

# Создаем папку для скачивания, если её нет
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Блокировка, чтобы скачивания не конфликтовали
download_lock = asyncio.Lock()

# Главное меню
keyboard = [
    ["🔍 Поиск по артисту", "🎵 Поиск по названию"],
    ["🎭 Найти по настроению", "⚙️ Настройки"]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎶 Добро пожаловать в EmoDJ — бот, который находит музыку по твоему настроению, артисту или названию!\n\n"
        "Выбери действие ниже 👇",
        reply_markup=markup
    )

# Обработка кнопок меню и сообщений
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
        await update.message.reply_text("🧠 Введи настроение (например: грустно, весело, мотивация):")
    elif text == "⚙️ настройки".lower():
        await update.message.reply_text("⚙️ Пока нет доступных настроек.")
    else:
        await process_query(update, context)

# Обработка поискового запроса
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
        await update.message.reply_text("❗ Пожалуйста, выбери действие в меню.")
        return

    search = VideosSearch(search_query, limit=1)
    result = search.result()

    if result['result']:
        video = result['result'][0]
        title = video['title']
        url = video['link']

        # Сохраняем данные трека, чтобы потом скачать
        context.user_data["last_track"] = {"title": title, "url": url}

        # Кнопки: ссылка и скачать MP3
        buttons = [
            [InlineKeyboardButton("🔗 Слушать на YouTube", url=url)],
            [InlineKeyboardButton("⬇️ Скачать MP3", callback_data="download_mp3")]
        ]
        await update.message.reply_text(
            f"🎧 Найдена песня: {title}\nЧто хочешь сделать?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await update.message.reply_text("❌ Ничего не найдено. Попробуй другой запрос.")

# Обработка кнопок inline (скачивание MP3)
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download_mp3":
        track = context.user_data.get("last_track")
        if not track:
            await query.edit_message_text("⚠️ Ошибка: Трек не найден.")
            return

        url = track["url"]
        title = track["title"]

        await query.edit_message_text(f"⬇️ Начинаю скачивание: {title} ... Это может занять несколько секунд.")

        # Блокируем скачивание, чтобы избежать конфликтов
        async with download_lock:
            try:
                yt = YouTube(url)
                audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()

                if not audio_stream:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Не удалось найти аудио поток.")
                    return

                # Уникальное имя файла
                file_name = f"downloads/{uuid.uuid4()}.mp3"
                audio_stream.download(output_path="downloads", filename=file_name.split('/')[-1])

                # Отправляем файл
                with open(file_name, "rb") as audio_file:
                    await context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio_file, title=title)

                os.remove(file_name)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Готово! Приятного прослушивания 🎶")

            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Ошибка при скачивании: {e}")

# Создаем и запускаем приложение
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
app.add_handler(CallbackQueryHandler(handle_callback))

app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 8443)),
    webhook_url=WEBHOOK_URL
)

