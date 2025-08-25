import os
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Get environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
BG_API_KEY = os.getenv("BG_API_KEY")

# ---------- Start Command ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Support Channel", url="https://t.me/bye_artist")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_animation(
        animation="https://files.catbox.moe/lhbsqt.mp4",
        caption=(
            "👋 <b>Welcome to BG Remove Bot!</b>\n\n"
            "📌 Send me any photo and I will remove its background for you."
        ),
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# ---------- Handle Photos ----------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_bytes = await file.download_as_bytearray()

        # Call remove.bg API
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": file_bytes},
            data={"size": "auto"},
            headers={"X-Api-Key": BG_API_KEY},
        )

        if response.status_code == 200:
            await update.message.reply_document(
                document=response.content,
                filename="bg_removed.png",
                caption="✅ Background removed successfully!"
            )
        else:
            await update.message.reply_text(
                "❌ Failed to remove background. Please check your API key or try again later."
            )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

# ---------- Main Function ----------
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()

if __name__ == "__main__":
    main()
    
