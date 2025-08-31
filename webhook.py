import os
import asyncio
from telegram import Bot

TOKEN = "8420133047:AAELZW2OkUan3pmw5X_6-NxeuiuZhl2cIg8"
WEBHOOK_URL = "https://telegram-bot-xuw2.onrender.com"  # your Render app domain

async def main():
    bot = Bot(token=TOKEN)

    # clear old webhook
    await bot.delete_webhook()

    # set new webhook
    await bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{TOKEN}")

    print("Webhook set to:", f"{WEBHOOK_URL}/webhook/{TOKEN}")

if __name__ == "__main__":
    asyncio.run(main())
