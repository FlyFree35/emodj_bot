import os
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 8080))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот! 😊")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

async def handle_request(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.update_queue.put(update)
    return web.Response()

web_app = web.Application()
web_app.router.add_post(WEBHOOK_PATH, handle_request)

async def on_startup(app_):
    webhook_url = os.environ.get("WEBHOOK_URL")
    await app.bot.set_webhook(url=webhook_url + WEBHOOK_PATH)

web_app.on_startup.append(on_startup)
app.run_web_app(web_app, port=PORT)
