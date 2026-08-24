import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
from bot_handler import dp, bot
from listener import start_listener, client as telethon_client
from database import init_db
from aiogram.types import BotCommand

ADMIN_ID = "6438818927"

async def setup_bot_commands(bot):
    commands = [
        BotCommand(command="start", description="Start Insider Finance bot"),
        BotCommand(command="subscribe", description="Verify or activate subscription"),
        BotCommand(command="setlang", description="Change broadcast language")
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        print(f"Failed to set bot commands: {e}")

@dp.startup()
async def on_startup():
    print("Initializing Database...")
    await init_db()
    
    print("Setting up bot commands...")
    await setup_bot_commands(bot)
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text="🟢 **Insider Finance System Started!**\nBoth the Listener and Broadcaster are now online.", parse_mode="Markdown")
    except Exception as e:
        print(f"Could not send startup message: {e}")
        
    print("Starting TELETHON Userbot (Listener)...")
    asyncio.create_task(start_listener())

@dp.shutdown()
async def on_shutdown():
    try:
        await bot.send_message(chat_id=ADMIN_ID, text="🔴 **Insider Finance System Stopped!**\nThe Listener and Broadcaster have been shut down.", parse_mode="Markdown")
    except Exception:
        pass
    finally:
        await telethon_client.disconnect()
        await bot.session.close()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
