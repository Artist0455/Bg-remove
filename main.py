import os
import requests
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, Animation
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes
)

# 🔑 Your API Key and Bot Token
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY", "YOUR_REMOVE_BG_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# 📌 /start command
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📢 Support Channel", url="https://t.me/YourChannel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Animation (GIF or MP4 link)
    animation_url = "https://media.giphy.com/media/du3J3cXyzhj75IOgvA/giphy.mp4"

    update.message.reply_animation(
        animation=animation_url,
        caption=(
            "👋 Welcome to <b>Background Remover Bot</b>!\n\n"
            "📸 Send me any photo and I will remove its background instantly.\n\n"
            "⚡ Powered by <b>Remove.bg API</b>"
        ),
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

# 📌 Background remove function
def remove_bg(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]  # Best quality photo
    file = context.bot.get_file(photo.file_id)
    file.download("input.jpg")

    with open("input.jpg", "rb") as f:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": f},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API_KEY},
        )

    if response.status_code == 200:
        with open("output.png", "wb") as out:
            out.write(response.content)
        update.message.reply_photo(
            photo=open("output.png", "rb"),
            caption="✅ Background removed successfully!"
        )
    else:
        update.message.reply_text(
            f"❌ Error {response.status_code}: {response.text}"
        )

# 📌 Main function
def main():
    app = Application.builder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


    updater.idle()

if __name__ == "__main__":
    main()
    
