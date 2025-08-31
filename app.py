import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from difflib import SequenceMatcher

# This is a development server warning. It's safe to ignore for this issue.
# The 500 error is caused by a problem in your webhook handler.
# 
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

def is_similar(a, b, threshold=0.7):
    return SequenceMatcher(None, a, b).ratio() > threshold

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user_message = update.message.text.strip().lower()
    if any(is_similar(user_message, q) for q in ACCEPTED_QUESTIONS):
        await update.message.reply_text("🚩 FLAG")
    else:
        await update.message.reply_text("I don't understand that.")

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- webhook route ---
# This part has been updated to handle async operations correctly.
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        if update:
            await application.process_update(update)
            return "ok"
        return "no update", 400
    except Exception as e:
        print(f"Webhook error: {e}")
        return "error", 500

# This part has been updated to set the webhook and run the application.
@app.route("/")
async def home():
    # Set the webhook to your render URL on startup
    await application.bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    return "Bot is running and webhook is set!"

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(home())
    loop.run_until_complete(app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000))))