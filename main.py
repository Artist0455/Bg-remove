import os
import logging
import asyncio
from io import BytesIO

import requests
from telegram import Update, InputFile
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
REMOVE_BG_API_KEY = os.getenv("4SLJ7cmvQVrgnmmcitHQs56Y")
REMOVE_BG_URL = "https://api.remove.bg/v1.0/removebg"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 <b>Background Remover Bot</b>\n\n"
        "मुझे कोई भी <b>फोटो</b> भेजो (या फोटो पर reply में “remove bg” लिखो), "
        "मैं background हटा कर <i>PNG</i> दे दूँगा.\n\n"
        "⚙️ Powered by <code>remove.bg</code>\n"
        "📌 Supported: Photos & image documents (jpg/png/webp)"
    )
    await update.message.reply_html(text)


async def _download_telegram_file_bytes(file_id: str, context: ContextTypes.DEFAULT_TYPE) -> bytes:
    """Safely fetch bytes of a Telegram file."""
    tg_file = await context.bot.get_file(file_id)
    # Build a direct download URL
    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{tg_file.file_path}"
    resp = requests.get(download_url, timeout=60)
    resp.raise_for_status()
    return resp.content


def _remove_bg(image_bytes: bytes) -> bytes:
    """Call remove.bg API and return processed PNG bytes."""
    headers = {"X-Api-Key": REMOVE_BG_API_KEY}
    files = {"image_file": ("image.png", image_bytes)}
    data = {"size": "auto"}  # full resolution within plan limits
    r = requests.post(REMOVE_BG_URL, headers=headers, files=files, data=data, timeout=120)
    if r.status_code == 200:
        return r.content
    # Try to parse error from API
    try:
        err = r.json()
    except Exception:
        err = r.text
    raise RuntimeError(f"remove.bg failed ({r.status_code}): {err}")


async def _process_photo_bytes(update: Update, context: ContextTypes.DEFAULT_TYPE, image_bytes: bytes):
    # typing / upload action
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)

    try:
        out_png = _remove_bg(image_bytes)
    except Exception as e:
        logger.exception("remove.bg error")
        await update.message.reply_text(
            f"❌ Background remove failed:\n{e}\n\n"
            "Please try a different image or smaller size."
        )
        return

    bio = BytesIO(out_png)
    bio.name = "removed.png"
    await update.message.reply_document(
        document=InputFile(bio, filename="removed.png"),
        caption="✅ Background removed!",
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get best quality photo
    if not update.message.photo:
        return
    photo = update.message.photo[-1]
    try:
        img_bytes = await _download_telegram_file_bytes(photo.file_id, context)
        await _process_photo_bytes(update, context, img_bytes)
    except Exception as e:
        logger.exception("photo handler error")
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        return
    # Allow only image docs
    if not (doc.mime_type and doc.mime_type.startswith("image/")):
        await update.message.reply_text("⚠️ Please send an image file (JPG/PNG/WebP).")
        return
    try:
        img_bytes = await _download_telegram_file_bytes(doc.file_id, context)
        await _process_photo_bytes(update, context, img_bytes)
    except Exception as e:
        logger.exception("document handler error")
        await update.message.reply_text(f"❌ Error: {e}")


async def removebg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """If user replies /removebg to a photo/document."""
    if update.message.reply_to_message:
        # Try from replied photo
        src = update.message.reply_to_message
        if src.photo:
            file_id = src.photo[-1].file_id
        elif src.document and src.document.mime_type and src.document.mime_type.startswith("image/"):
            file_id = src.document.file_id
        else:
            await update.message.reply_text("Reply to an image message, please.")
            return
        try:
            img_bytes = await _download_telegram_file_bytes(file_id, context)
            await _process_photo_bytes(update, context, img_bytes)
        except Exception as e:
            logger.exception("removebg command error")
            await update.message.reply_text(f"❌ Error: {e}")
    else:
        await update.message.reply_text("Send a photo or reply /removebg to an image message.")


def main():
    if not BOT_TOKEN or not REMOVE_BG_API_KEY:
        raise SystemExit("Please set BOT_TOKEN and REMOVE_BG_API_KEY environment variables.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("removebg", removebg_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    logger.info("Bot started.")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
