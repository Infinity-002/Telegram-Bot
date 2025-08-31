from telegram import Bot
import os

TOKEN = '8420133047:AAELZW2OkUan3pmw5X_6-NxeuiuZhl2cIg8'
WEBHOOK_URL = 'https://telegram-bot-xuw2.onrender.com'

bot = Bot(token=TOKEN)
bot.delete_webhook()
bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{TOKEN}")
print("Webhook set to:", f"{WEBHOOK_URL}/webhook/{TOKEN}")
