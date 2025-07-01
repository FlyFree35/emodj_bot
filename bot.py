import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Получаем токен из переменных окружения (или вставь напрямую)
TOKEN = os.getenv("BOT_TOKEN")

# Меню кнопок
keyboard = [
    ["🔍 Поиск по артисту", "🎵 Поиск по названию"],
    ["🎭 Найти по настроению", "⚙️ Настройки"]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎶 Добро пожаловать в EmoDJ — бот, который находит музыку по твоему настроению, артисту или названию!\n\n"
        "Выбери действие ниже 👇",
        reply_markup=markup
    )

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

# Запуск через Webhook
app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 8443)),
    webhook_url="https://emodj-bot-1.onrender.com"
)

