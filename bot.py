import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Порт, который Render указывает через переменные окружения
PORT = int(os.environ.get("PORT", 8443))

# Токен и Webhook URL тоже через переменные окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой Emo-DJ бот!")

# Создаем бота
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Добавляем хендлер на команду /start
app.add_handler(CommandHandler("start", start))

# Запускаем через Webhook (именно так нужно на Render)
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=WEBHOOK_URL
)
