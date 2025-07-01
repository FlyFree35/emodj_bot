import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Получение токена и порта от Render
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))
WEBHOOK_URL = "https://emodj-bot-1.onrender.com"  # Твой адрес

# Музыка по настроению
MOOD_MUSIC = {
    "Грустно 😢": [
        "https://youtu.be/Ho32Oh6b4jc",
        "https://youtu.be/K4DyBUG242c"
    ],
    "Весело 😊": [
        "https://youtu.be/ZbZSe6N_BXs",
        "https://youtu.be/3JZ4pnNtyxQ"
    ],
    "Спокойно 😌": [
        "https://youtu.be/1ZYbU82GVz4",
        "https://youtu.be/d-diB65scQU"
    ],
    "Энергично 💪": [
        "https://youtu.be/fLexgOxsZu0",
        "https://youtu.be/hT_nvWreIhg"
    ],
    "Романтично ❤️": [
        "https://youtu.be/450p7goxZqg",
        "https://youtu.be/mWRsgZuwf_8"
    ],
    "Мотивирующе 🔥": [
        "https://youtu.be/2vjPBrBU-TM",
        "https://youtu.be/dQw4w9WgXcQ"
    ]
}

# Клавиатура настроений
def get_mood_keyboard():
    keyboard = [[KeyboardButton(mood)] for mood in MOOD_MUSIC.keys()]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Привет! Я музыкальный бот по настроению.\n\n"
        "Выбери, как ты себя чувствуешь, и я подберу тебе трек.",
        reply_markup=get_mood_keyboard()
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Команды:\n"
        "/start — показать меню\n"
        "/help — помощь\n"
        "/about — о боте"
    )

# /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎧 Я — бот, который подбирает музыку по твоему настроению.\n"
        "Просто выбери настроение из меню, и наслаждайся треком!"
    )

# Обработка выбора настроения
async def mood_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mood = update.message.text
    tracks = MOOD_MUSIC.get(mood)
    if tracks:
        for link in tracks:
            await update.message.reply_text(link)
    else:
        await update.message.reply_text("❌ Я не понял настроение. Пожалуйста, выбери из меню ниже.")

# Инициализация бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("about", about))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mood_handler))

# Запуск на Render
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=WEBHOOK_URL
)
