import asyncio
from sqlalchemy.future import select
from models import Subscription
from database import AsyncSessionLocal
from translator import translate_text
from bot_handler import bot

async def run_test():
    message_text = "🔥 **URGENT MARKET UPDATE**\n\nFederal Reserve announces a surprise 50 bps rate cut. Markets are rallying globally, with SPX up 2.4% and Gold hitting record highs. Traders are advised to monitor volatility closely over the next 4 hours."
    
    print("Running test broadcast...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Subscription).where(Subscription.is_active == True))
        subs = result.scalars().all()
        
        if not subs:
            print("No active subscriptions found in the database.")
            return
            
        for sub in subs:
            print(f"Broadcasting to {sub.group_name} ({sub.group_id}) with languages: {sub.target_language}")
            langs = sub.target_language.split(",")
            combined_parts = []
            for lang in langs:
                if not lang:
                    continue
                try:
                    if sub.is_premium and lang != "en":
                        chunk = translate_text(message_text, lang)
                    else:
                        chunk = message_text
                    
                    flag = {"en":"🇬🇧", "ru":"🇷🇺", "es":"🇪🇸", "uz":"🇺🇿", "tr":"🇹🇷", "zh-cn":"🇨🇳"}.get(lang, "🌐")
                    combined_parts.append(f"{flag} **{lang.upper()}**\n{chunk}")
                except Exception as e:
                    print(f"❌ Failed to translate test for {lang}: {e}")
            
            if combined_parts:
                try:
                    final_message = "\n\n".join(combined_parts)
                    await bot.send_message(chat_id=sub.group_id, text=f"**[COMBINED TEST BROADCAST]**\n\n{final_message}", parse_mode="Markdown")
                    print(f"✅ Sent combined test to {sub.group_name}")
                    await asyncio.sleep(1.5) # Prevent Google Translate free tier limits
                except Exception as e:
                    print(f"❌ Failed to send test to {sub.group_name}: {e}")
                    
    print("Test broadcast complete.")

if __name__ == "__main__":
    asyncio.run(run_test())
