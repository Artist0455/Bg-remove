import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token & API key from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
REMOVE_BG_API = os.getenv("REMOVE_BG_API")  # put your remove.bg API key here

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Support Channel", url="https://t.me/bye_artist")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_animation(
        animation="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
        caption="👋 Welcome to <b>Background Remover Bot</b>!\n\n"
                "Just send me any photo and I will remove its background for you ✨",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# Function to remove background
async def remove_bg(image_file_path):
    with open(image_file_path, "rb") as f:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": f},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API},
        )
    if response.status_code == 200:
        output_path = "no_bg.png"
        with open(output_path, "wb") as out:
            out.write(response.content)
        return output_path
    else:
        return None

# Handle images
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    input_path = "input.png"
    await file.download_to_drive(input_path)

    await update.message.reply_text("⏳ Removing background... Please wait!")

    output_path = await remove_bg(input_path)

    if output_path:
        await update.message.reply_document(document=open(output_path, "rb"))
    else:
        await update.message.reply_text("❌ Failed to remove background. Please try again later.")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()

if __name__ == "__main__":
    main()
    
