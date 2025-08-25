import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("✅ Bot is running!")

def run_http_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running")
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # HTTP server ko alag thread me chalao
    threading.Thread(target=run_http_server, daemon=True).start()

    # Bot polling chalao
    app.run_polling()

if __name__ == "__main__":
    main()
    
