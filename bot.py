import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))  # Render сам задаёт порт

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я музыкальный бот 🎶")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

WEBHOOK_URL = "https://emodj-bot-1.onrender.com"  # твой адрес

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=WEBHOOK_URL
)
