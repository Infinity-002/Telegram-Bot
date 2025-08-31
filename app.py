import os
import asyncio
import threading
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from difflib import SequenceMatcher

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# --- handlers ---
ACCEPTED_QUESTIONS = [
    "was this necessary?",
    "do we really need this?",
    "is this important?",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot. Send me a question.")

def is_similar(a, b, threshold=0.7):
    return SequenceMatcher(None, a, b).ratio() > threshold

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user_message = update.message.text.strip().lower()
    if any(is_similar(user_message, q) for q in ACCEPTED_QUESTIONS):
        await update.message.reply_text("🚩 FLAG")
        
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
# Removed undefined 'echo' handler to fix NameError

# --- webhook route ---
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        if update:
            application.update_queue.put_nowait(update)
            return "ok"
        return "no update", 400
    except Exception as e:
        print(f"Webhook error: {e}")
        return "error", 500

@app.route("/")
def home():
    return "Bot is running!"

def run_telegram():
    asyncio.run(application.initialize())
    asyncio.run(application.start())
    # keep the bot running forever
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    # Start Telegram in background thread
    threading.Thread(target=run_telegram, daemon=True).start()
    # Start Flask server
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
