import os
import asyncio
from telethon import TelegramClient, events
from sqlalchemy.future import select
from models import Subscription
from database import AsyncSessionLocal
from translator import translate_text
from bot_handler import bot
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL")

# Session file will be created in the current directory
client = TelegramClient('userbot_session', API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def new_message_handler(event):
    message_text = event.message.message
    if not message_text:
        return # Skip media without text for now
        
    print(f"New news received: {message_text[:50]}...")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Subscription).where(
                Subscription.is_active == True,
                Subscription.status == "active"
            )
        )
        subs = result.scalars().all()
        
        if not subs:
            return

        # 1. Gather all unique languages required
        needed_langs = set()
        for sub in subs:
            if sub.target_language:
                needed_langs.update(sub.target_language.split(","))
        
        # 2. Pre-translate the message for all required languages
        translations = {"en": message_text}
        for lang in needed_langs:
            if lang and lang != "en":
                translations[lang] = translate_text(message_text, lang)
                await asyncio.sleep(0.5) # Prevent translation API rate limits
                
        # 3. Broadcast to each group using the pre-translated cache
        for sub in subs:
            try:
                langs = sub.target_language.split(",")
                combined_parts = []
                
                for lang in langs:
                    if not lang:
                        continue
                    
                    chunk = translations.get(lang, message_text)
                    flag = {"en":"🇬🇧", "ru":"🇷🇺", "es":"🇪🇸", "uz":"🇺🇿", "tr":"🇹🇷", "zh-cn":"🇨🇳"}.get(lang, "🌐")
                    combined_parts.append(f"{flag} **{lang.upper()}**\n{chunk}")
                    
                if combined_parts:
                    final_message = "\n\n".join(combined_parts)
                    await bot.send_message(chat_id=sub.group_id, text=final_message, parse_mode="Markdown")
                    print(f"✅ Sent combined broadcast to {sub.group_name}")
                    await asyncio.sleep(1.0) # Prevent Telegram API rate limits
                
            except Exception as e:
                print(f"❌ Failed to send to {sub.group_name}: {e}")

async def start_listener():
    await client.start()
    print("🚀 Userbot Listener is running! Monitoring SM_News_24h...")
    await client.run_until_disconnected()
