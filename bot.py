from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

# Музыкальные плейлисты по настроению
playlists = {
    "грустно": {
        "youtube": ["https://youtu.be/z3wAjJXbYzA"],
        "spotify": ["https://open.spotify.com/track/6IcEdOYpRxBVuFzqZzP06B"]
    },
    "весело": {
        "youtube": ["https://youtu.be/dQw4w9WgXcQ"],
        "spotify": ["https://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb"]
    },
    "мотивация": {
        "youtube": ["https://youtu.be/2vjPBrBU-TM"],
        "spotify": ["https://open.spotify.com/track/0VgkVdmE4gld66l8iyGjgx"]
    },
    "романтика": {
        "youtube": ["https://youtu.be/JGwWNGJdvx8"],
        "spotify": ["https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3"]
    },
    "спорт": {
        "youtube": ["https://youtu.be/6fVE8kSM43I"],
        "spotify": ["https://open.spotify.com/track/2KH16WveTQWT6KOG9Rg6e2"]
    },
    "злость": {
        "youtube": ["https://youtu.be/04F4xlWSFh0"],
        "spotify": ["https://open.spotify.com/track/5sNESr6pQfIhL3krM8CtZn"]
    }
}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Напиши /mood <настроение>, и я пришлю музыку! 🎶\n"
        "Например: /mood грустно\n"
        "Доступные настроения: /moods"
    )

# /moods
async def moods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mood_list = "\n".join(playlists.keys())
    await update.message.reply_text(f"🎭 Доступные настроения:\n{mood_list}")

# /mood <настроение>
async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        mood = context.args[0].lower()
        if mood in playlists:
            yt_links = '\n'.join(playlists[mood]["youtube"])
            sp_links = '\n'.join(playlists[mood]["spotify"])
            await update.message.reply_text(
                f"🎧 *{mood}*\n\nYouTube:\n{yt_links}\n\nSpotify:\n{sp_links}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("Такого настроения нет. Напиши /moods чтобы посмотреть список.")
    else:
        await update.message.reply_text("Напиши настроение после команды. Пример: /mood весело")

# создаём и запускаем бота
app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mood", mood))
app.add_handler(CommandHandler("moods", moods))
app.run_polling()

