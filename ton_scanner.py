import asyncio
import aiohttp
from shared import PENDING_TON_PAYMENTS
from bot_handler import bot
from database import AsyncSessionLocal
from models import PaymentHistory
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

WALLET = "UQCyX_cds5H0YnciaKaiWw7N3hfsLmpbOES851PUqbqkqHBR"

async def scan_ton_blockchain():
    url = f"https://toncenter.com/api/v2/getTransactions?address={WALLET}&limit=10"
    processed_hashes = set()
    
    print("Starting TON Blockchain Scanner...")
    
    while True:
        try:
            if not PENDING_TON_PAYMENTS:
                await asyncio.sleep(10)
                continue
                
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        await asyncio.sleep(5)
                        continue
                        
                    data = await response.json()
                    
                    if not data.get("ok") or not data.get("result"):
                        await asyncio.sleep(10)
                        continue
                        
                    transactions = data["result"]
                    for tx in transactions:
                        tx_hash = tx.get("transaction_id", {}).get("hash")
                        if not tx_hash or tx_hash in processed_hashes:
                            continue
                            
                        processed_hashes.add(tx_hash)
                        if len(processed_hashes) > 1000:
                            processed_hashes.clear() # Prevent memory leak
                            
                        in_msg = tx.get("in_msg")
                        if not in_msg:
                            continue
                            
                        msg_data = in_msg.get("message")
                        if not msg_data:
                            continue
                            
                        # The message is usually a string memo
                        for memo, payment_info in list(PENDING_TON_PAYMENTS.items()):
                            if memo in msg_data:
                                # Found it!
                                user_id = payment_info["user_id"]
                                add_url = payment_info["add_url"]
                                ui_lang = payment_info["ui_lang"]
                                amount = payment_info["amount"]
                                
                                # Remove from pending
                                del PENDING_TON_PAYMENTS[memo]
                                
                                # DB
                                try:
                                    async with AsyncSessionLocal() as db_session:
                                        new_payment = PaymentHistory(
                                            user_id=str(user_id),
                                            amount=int(amount * 1000000),
                                            currency="TON",
                                            payment_method="ton_transfer"
                                        )
                                        db_session.add(new_payment)
                                        await db_session.commit()
                                except Exception as e:
                                    print(f"Failed to record TON payment in database: {e}")
                                
                                msg = f"✅ **TON Payment Received!** ({amount} TON)\n\nYour subscription is now active for 1 month. Click the button below to add Insider Finance to your group or channel."
                                
                                kb = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="➕ Add to Group/Channel", url=add_url)],
                                    [InlineKeyboardButton(text="🔙 Back to Main", callback_data=f"lang_{ui_lang}")]
                                ])
                                
                                try:
                                    await bot.send_message(chat_id=user_id, text=msg, reply_markup=kb, parse_mode="Markdown")
                                    print(f"Successfully activated TON subscription for user {user_id}")
                                except Exception as e:
                                    print(f"Failed to notify user {user_id} of TON payment: {e}")
                                    
        except Exception as e:
            print(f"Error scanning TON blockchain: {e}")
            
        await asyncio.sleep(10)
