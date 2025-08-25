import os
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
BG_API_KEY = os.getenv("BG_API_KEY")  # Background remove website ka API key
SUPPORT_CHANNEL = "https://t.me/bye_artist"
ANIMATION_URL = "https://files.catbox.moe/lhbsqt.mp4"  # Example animation

# ---------- START COMMAND ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Join Support Channel", url=SUPPORT_CHANNEL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_animation(
        animation=ANIMATION_URL,
        caption="👋 Welcome to **Background Remover Bot!**\n\n📷 Send me a photo and I'll remove its background instantly.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ---------- PHOTO HANDLER ----------
async def remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ Please send a valid photo.")
        return

    # Get the highest quality photo
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    # Call background removal API
    url = "https://api.remove.bg/v1.0/removebg"
    response = requests.post(
        url,
        files={"image_file": photo_bytes},
        data={"size": "auto"},
        headers={"X-Api-Key": BG_API_KEY},
    )

    if response.status_code == 200:
        with open("no_bg.png", "wb") as f:
            f.write(response.content)

        await update.message.reply_document(
            document=InputFile("no_bg.png"),
            caption="✅ Background removed successfully!"
        )
    else:
        await update.message.reply_text("❌ Failed to remove background. Check API key.")

# ---------- DUMMY HTTP SERVER ----------
def run_http_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running on Render Free plan!")
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, remove_bg))

    # Start dummy HTTP server in thread
    threading.Thread(target=run_http_server, daemon=True).start()

    # Run bot polling
    app.run_polling()

if __name__ == "__main__":
    main()
    
