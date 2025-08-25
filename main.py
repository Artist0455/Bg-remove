import os
import logging
import requests
import filetype   # imghdr ke jagah ye use hoga
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")  # Remove.bg ya koi bhi API key

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Support Channel", url="https://t.me/YourChannelLink")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_animation(
        animation="https://media.giphy.com/media/xT9IgzoKnwFNmISR8I/giphy.gif",
        caption="👋 Hi! Send me a photo and I'll remove its background instantly!",
        reply_markup=reply_markup
    )

# Background remove function
async def remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Please send a valid photo.")
        return

    file = await update.message.photo[-1].get_file()
    file_path = "input.jpg"
    await file.download_to_drive(file_path)

    # filetype se check karenge
    kind = filetype.guess(file_path)
    if not kind or kind.mime.split("/")[0] != "image":
        await update.message.reply_text("❌ File is not a valid image.")
        return

    with open(file_path, "rb") as f:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": f},
            data={"size": "auto"},
            headers={"X-Api-Key": API_KEY},
        )

    if response.status_code == 200:
        output_path = "output.png"
        with open(output_path, "wb") as out:
            out.write(response.content)
        await update.message.reply_document(document=open(output_path, "rb"))
    else:
        await update.message.reply_text("❌ Failed to remove background. Check API key.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, remove_bg))
    app.run_polling()

if __name__ == "__main__":
    main()
    
