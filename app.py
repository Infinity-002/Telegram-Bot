import os
from flask import Flask, request
from telegram.ext import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# --- handlers ---
from difflib import SequenceMatcher

ACCEPTED_QUESTIONS = [
    "was this necessary?",
    "do we really need this?",
    "is this important?",
]

def is_similar(a, b, threshold=0.7):
    return SequenceMatcher(None, a, b).ratio() > threshold

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip().lower()
    if any(is_similar(user_message, q) for q in ACCEPTED_QUESTIONS):
        await update.message.reply_text("🚩 FLAG")
    else:
        await update.message.reply_text("I don't understand that.")

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))