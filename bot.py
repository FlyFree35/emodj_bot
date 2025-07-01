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
import yt_dlp  # Используем вместо pytube
import uuid

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
        "🎶 Добро пожаловать в EmoDJ!\n"
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
        await update.message.reply_text("🧠 Введи настроение (\u043dапр.: весело, грустно):")
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
        await update.message.reply_text("\u2757 \u0412\u044b\u0431\u0435\u0440\u0438 \u0441\u043d\u0430\u0447\u0430\u043b\u0430 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u0432 \u043c\u0435\u043d\u044e.")
        return

    search = VideosSearch(search_query, limit=1)
    result = search.result()

    if result['result']:
        video = result['result'][0]
        title = video['title']
        url = video['link']

        context.user_data['last_track'] = {'title': title, 'url': url}

        buttons = [
            [InlineKeyboardButton("\ud83d\udd17 Слушать на YouTube", url=url)],
            [InlineKeyboardButton("\u2b07\ufe0f Скачать MP3", callback_data="download_mp3")]
        ]

        await update.message.reply_text(
            f"\ud83c\udfb5 \u041d\u0430\u0439\u0434\u0435\u043d\u0430 \u043f\u0435\u0441\u043d\u044f: {title}\n\u0427\u0442\u043e \u0445\u043e\u0447\u0435\u0448\u044c \u0441\u0434\u0435\u043b\u0430\u0442\u044c?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await update.message.reply_text("\u274c \u041d\u0438\u0447\u0435\u0433\u043e \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439 \u0434\u0440\u0443\u0433\u043e\u0439 \u0437\u0430\u043f\u0440\u043e\u0441.")

# Inline кнопка: Скачивание mp3
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download_mp3":
        track = context.user_data.get("last_track")
        if not track:
            await query.edit_message_text("⚠️ Ошибка: трек не найден.")
            return

        url = track["url"]
        title = track["title"]

        await query.edit_message_text(f"⬇️ Скачиваю: {title} ...")

        async with download_lock:
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'downloads/%(id)s.%(ext)s',
                    'quiet': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = f"downloads/{info['id']}.mp3"

                with open(filename, "rb") as audio:
                    await context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio, title=title)

                os.remove(filename)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Готово!")
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Ошибка: {e}")

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

