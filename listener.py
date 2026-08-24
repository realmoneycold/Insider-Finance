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

import re
from aiogram.types import FSInputFile
import os
from shared import PENDING_HUMO_PAYMENTS
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Session file will be created in the current directory
client = TelegramClient('userbot_session', API_ID, API_HASH)

from models import Subscription, PaymentHistory

@client.on(events.NewMessage(chats='HUMOcardbot'))
async def humo_payment_handler(event):
    message_text = event.message.message
    if not message_text:
        return
        
    print(f"Humo bot message: {message_text}")
    # Example: ➕ 30.123,00 UZS
    match = re.search(r"➕\s*([\d\.,]+)\s*UZS", message_text)
    if match:
        amount_str = match.group(1).replace(".", "").replace(",", "")
        try:
            clean_str = match.group(1).replace(".", "")
            if "," in clean_str:
                amount = int(clean_str.split(",")[0])
            else:
                amount = int(clean_str)
        except Exception as e:
            print("Could not parse amount", e)
            return
            
        print(f"Detected payment of {amount} UZS")
        if amount in PENDING_HUMO_PAYMENTS:
            payment_info = PENDING_HUMO_PAYMENTS.pop(amount)
            user_id = payment_info["user_id"]
            add_url = payment_info["add_url"]
            ui_lang = payment_info["ui_lang"]
            
            # Record payment in database!
            try:
                async with AsyncSessionLocal() as session:
                    new_payment = PaymentHistory(
                        user_id=str(user_id),
                        amount=amount,
                        payment_method="humo"
                    )
                    session.add(new_payment)
                    await session.commit()
            except Exception as e:
                print(f"Failed to record payment in database: {e}")
            
            from translations import UI_TRANSLATIONS
            t = UI_TRANSLATIONS.get(ui_lang, UI_TRANSLATIONS["en"])
            
            msg = t["pay_success"]
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t["btn_add_chat"], url=add_url)],
                [InlineKeyboardButton(text=t["btn_back_main"], callback_data=f"lang_{ui_lang}")]
            ])
            try:
                await bot.send_message(chat_id=user_id, text=msg, reply_markup=kb, parse_mode="Markdown")
                print(f"Successfully activated subscription for user {user_id}")
            except Exception as e:
                print(f"Failed to notify user {user_id}: {e}")

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def new_message_handler(event):
    message_text = event.message.message
    if not message_text:
        return # Skip media without text for now
        
    # ANTI-AD / SPAM FILTER
    blocked_keywords = [
        "weekly results",
        "srosh mayi",
        "@sroshmayi",
        "premium signals",
        "secure your access",
        "quadrupled",
        "if you aren't in the",
        "sroshmayi_bot"
    ]
    
    message_lower = message_text.lower()
    for keyword in blocked_keywords:
        if keyword in message_lower:
            print(f"🛑 Blocked promotional message containing: '{keyword}'")
            return
            
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

        media_path = None
        if event.message.media and event.message.photo:
            os.makedirs("temp_media", exist_ok=True)
            media_path = await event.message.download_media(file="temp_media/")

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
                    if media_path and event.message.photo:
                        try:
                            photo = FSInputFile(media_path)
                            # Send photo first without caption to avoid 1024 char limit
                            await bot.send_photo(chat_id=sub.group_id, photo=photo)
                            # Then send the full translated text
                            await bot.send_message(chat_id=sub.group_id, text=final_message, parse_mode="Markdown")
                        except Exception as photo_e:
                            print(f"Could not send photo: {photo_e}")
                            await bot.send_message(chat_id=sub.group_id, text=final_message, parse_mode="Markdown")
                    else:
                        await bot.send_message(chat_id=sub.group_id, text=final_message, parse_mode="Markdown")
                    print(f"✅ Sent combined broadcast to {sub.group_name}")
                    await asyncio.sleep(1.0) # Prevent Telegram API rate limits
                
            except Exception as e:
                print(f"❌ Failed to send to {sub.group_name}: {e}")
                
        if media_path and os.path.exists(media_path):
            os.remove(media_path)

async def start_listener():
    await client.start()
    print("🚀 Userbot Listener is running! Monitoring SM_News_24h...")
    await client.run_until_disconnected()
