import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from youtubesearchpython import VideosSearch

# Токен бота
TOKEN = os.getenv("BOT_TOKEN")

# Кнопки меню
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

# Обработка текста кнопок и сообщений
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text == "🔍 поиск по артисту".lower():
        await update.message.reply_text("Напиши имя исполнителя 🎤")
    elif text == "🎵 поиск по названию".lower():
        await update.message.reply_text("Напиши название песни 🎶")
    elif text == "🎭 найти по настроению".lower():
        await update.message.reply_text("Напиши настроение: грустно, весело, мотивация, расслабиться и т.д.")
    elif text == "⚙️ настройки".lower():
        await update.message.reply_text("Пока нет доступных настроек ⚙️")
    else:
        await search_song(update, context)

# Поиск трека по тексту
async def search_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    search = VideosSearch(query, limit=1)
    result = search.result()

    if result['result']:
        video = result['result'][0]
        title = video['title']
        url = video['link']
        await update.message.reply_text(f"🎧 {title}\n🔗 {url}")
    else:
        await update.message.reply_text("❌ Ничего не найдено. Попробуй другой запрос.")

# Сборка приложения
app = ApplicationBuilder().token(TOKEN).build()

# Обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

# Запуск через Webhook (Render)
app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 8443)),
    webhook_url="https://emodj-bot-1.onrender.com"
)
