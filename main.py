import os
import requests
from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
REMOVE_BG_API = os.getenv("REMOVE_BG_API")  # तुम्हें remove.bg API key डालनी होगी
REMOVE_BG_URL = "https://api.remove.bg/v1.0/removebg"

SUPPORT_CHANNEL = "https://t.me/YourSupportChannel"
BOT_NAME = "🖼 Background Remover Bot"


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Support Channel", url= https://t.me/bye_Artist)],
        [InlineKeyboardButton("➕ Add me to Group", url=f"https://t.me/{context.bot.username}?startgroup=true")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_animation(
        animation="https://files.catbox.moe/lhbsqt.mp4",  # कोई भी gif डाल सकते हो
        caption=f"👋 Hello {update.effective_user.first_name}!\n\n"
                f"I am {BOT_NAME}.\n"
                f"Just send me any image & I will remove its background ✨",
        reply_markup=reply_markup
    )


# Image background remover
async def remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Please send a valid photo.")
        return

    file_id = update.message.photo[-1].file_id
    file = await context.bot.get_file(file_id)
    file_path = file.file_path

    # Send to remove.bg API
    response = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": requests.get(file_path).content},
        data={"size": "auto"},
        headers={"X-Api-Key": REMOVE_BG_API},
    )

    if response.status_code == 200:
        with open("no_bg.png", "wb") as f:
            f.write(response.content)

        await update.message.reply_document(InputFile("no_bg.png"))
        os.remove("no_bg.png")
    else:
        await update.message.reply_text("⚠️ Failed to remove background. Check API key or try again.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, remove_bg))

    app.run_polling()


if __name__ == "__main__":
    main()
    
