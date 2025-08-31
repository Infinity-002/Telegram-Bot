import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from difflib import SequenceMatcher

# Use environment variables for the token and webhook URL
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# --- Handlers ---
ACCEPTED_QUESTIONS = [
    "was this necessary?",
    "do we really need this?",
    "is this important?",
]

def is_similar(a, b, threshold=0.7):
    """
    Checks if two strings are similar based on a threshold.
    """
    return SequenceMatcher(None, a, b).ratio() > threshold

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles incoming text messages from users.
    """
    if not update.message:
        return
    user_message = update.message.text.strip().lower()
    if any(is_similar(user_message, q) for q in ACCEPTED_QUESTIONS):
        await update.message.reply_text("🚩 FLAG")
    else:
        await update.message.reply_text("I don't understand that.")

async def main():
    """
    Sets up the bot application and starts the webhook runner.
    """
    # Create the application with the bot token
    application = Application.builder().token(TOKEN).build()

    # Add the message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Check for the required environment variables
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set.")
    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL environment variable not set.")

    # Get the port from the environment, defaulting to 5000
    port = int(os.getenv("PORT", 5000))

    # Start the webhook server.
    # This single method handles all the web server, update processing, and async logic.
    await application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    # Check if an event loop is already running. This is a common issue with
    # some hosting platforms that might wrap the startup command.
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "This event loop is already running" in str(e):
            # If a loop is running, get it and run the main coroutine.
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
        else:
            # Re-raise the exception if it's not the one we expect.
            raise e