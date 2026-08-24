import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, ADMINISTRATOR
from aiogram.types import ChatMemberUpdated
from sqlalchemy.future import select
from models import Subscription
from database import AsyncSessionLocal
from dotenv import load_dotenv

PENDING_CHANNEL_SETUPS = {}

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

BOT_USERNAME = None

UI_TRANSLATIONS = {
    "en": {
        "text": (
            "📊 **About Insider Finance**\n\n"
            "Insider Finance is an institutional-grade financial news terminal. We deliver real-time market news, "
            "breaking updates, economic events, and vital trading signals.\n\n"
            "This bot is specifically designed to be added to your trading **Groups and Channels**. "
            "Once added, it will automatically broadcast all critical market intelligence directly to your community in your preferred language!\n\n"
            "👇 Click below to configure and add the bot to your community or join our official channel:"
        ),
        "btn_group": "➕ Add to Group",
        "btn_chan": "➕ Add to Channel",
        "btn_official": "📢 Official Channel",
        "select_langs": "👇 **Please select ALL the languages you want the news to be translated into for your group/channel:**",
        "btn_add_final": "✅ Continue & Add Bot",
        "connected_success": "✅ **Successfully Connected!**\n\nInsider Finance has been successfully added to your group/channel. You will now receive automated broadcasts.",
        "btn_back_main": "🔙 Back to Main"
    },
    "ru": {
        "text": (
            "📊 **О Insider Finance**\n\n"
            "Insider Finance — это финансовый новостной терминал институционального уровня. Мы предоставляем рыночные новости в реальном времени, "
            "срочные обновления, экономические события и важные торговые сигналы.\n\n"
            "Этот бот специально разработан для добавления в ваши торговые **Группы и Каналы**. "
            "После добавления он будет автоматически транслировать всю критически важную рыночную информацию прямо в ваше сообщество!\n\n"
            "👇 Нажмите ниже, чтобы настроить и добавить бота в свое сообщество или присоединиться к нашему официальному каналу:"
        ),
        "btn_group": "➕ Добавить в Группу",
        "btn_chan": "➕ Добавить в Канал",
        "btn_official": "📢 Официальный Канал",
        "select_langs": "👇 **Пожалуйста, выберите ВСЕ языки, на которые вы хотите переводить новости для вашей группы/канала:**",
        "btn_add_final": "✅ Продолжить и Добавить",
        "connected_success": "✅ **Успешно подключено!**\n\nInsider Finance был успешно добавлен в вашу группу/канал. Теперь вы будете получать автоматические трансляции.",
        "btn_back_main": "🔙 На главную"
    },
    "es": {
        "text": (
            "📊 **Sobre Insider Finance**\n\n"
            "Insider Finance es un terminal de noticias financieras de nivel institucional. Ofrecemos noticias del mercado en tiempo real, "
            "actualizaciones de última hora, eventos económicos y señales comerciales vitales.\n\n"
            "Este bot está diseñado específicamente para ser agregado a tus **Grupos y Canales** de trading. "
            "Una vez agregado, transmitirá automáticamente toda la inteligencia de mercado crítica directamente a tu comunidad.\n\n"
            "👇 Haz clic abajo para configurar y agregar el bot a tu comunidad o unirte a nuestro canal oficial:"
        ),
        "btn_group": "➕ Añadir al Grupo",
        "btn_chan": "➕ Añadir al Canal",
        "btn_official": "📢 Canal Oficial",
        "select_langs": "👇 **Por favor, selecciona TODOS los idiomas a los que deseas traducir las noticias para tu grupo/canal:**",
        "btn_add_final": "✅ Continuar y Añadir Bot",
        "connected_success": "✅ **¡Conectado con éxito!**\n\nInsider Finance se ha agregado correctamente a tu grupo/canal. Ahora recibirás transmisiones automáticas.",
        "btn_back_main": "🔙 Volver al inicio"
    },
    "uz": {
        "text": (
            "📊 **Insider Finance haqida**\n\n"
            "Insider Finance - bu professional darajadagi moliyaviy yangiliklar terminali. Biz real vaqt rejimida bozor yangiliklari, "
            "so'nggi xabarlar, iqtisodiy voqealar va muhim savdo signallarini yetkazib beramiz.\n\n"
            "Ushbu bot sizning savdo **Guruhlaringiz va Kanallaringizga** qo'shish uchun maxsus ishlab chiqilgan. "
            "Qo'shilgandan so'ng, u avtomatik ravishda barcha muhim bozor ma'lumotlarini to'g'ridan-to'g'ri hamjamiyatingizga uzatadi!\n\n"
            "👇 Botni sozlash va hamjamiyatingizga qo'shish yoki rasmiy kanalimizga qo'shilish uchun quyidagi tugmalarni bosing:"
        ),
        "btn_group": "➕ Guruhga qo'shish",
        "btn_chan": "➕ Kanalga qo'shish",
        "btn_official": "📢 Rasmiy Kanal",
        "select_langs": "👇 **Iltimos, guruhingiz/kanalingiz uchun yangiliklar tarjima qilinishini xohlagan BARCHA tillarni tanlang:**",
        "btn_add_final": "✅ Davom etish va Qo'shish",
        "connected_success": "✅ **Muvaffaqiyatli ulandi!**\n\nInsider Finance guruhingiz/kanalingizga muvaffaqiyatli qo'shildi. Endi siz avtomatik tarzda yangiliklarni qabul qilasiz.",
        "btn_back_main": "🔙 Asosiyga qaytish"
    },
    "tr": {
        "text": (
            "📊 **Insider Finance Hakkında**\n\n"
            "Insider Finance, kurumsal düzeyde bir finansal haber terminalidir. Gerçek zamanlı piyasa haberleri, "
            "son dakika güncellemeleri, ekonomik etkinlikler ve hayati ticaret sinyalleri sunuyoruz.\n\n"
            "Bu bot, ticaret **Grup ve Kanallarınıza** eklenmek üzere özel olarak tasarlanmıştır. "
            "Eklendikten sonra, tüm kritik piyasa istihbaratını otomatik olarak doğrudan topluluğunuza yayınlayacaktır!\n\n"
            "👇 Botu yapılandırmak ve topluluğunuza eklemek veya resmi kanalımıza katılmak için aşağıya tıklayın:"
        ),
        "btn_group": "➕ Gruba Ekle",
        "btn_chan": "➕ Kanala Ekle",
        "btn_official": "📢 Resmi Kanal",
        "select_langs": "👇 **Lütfen grubunuz/kanalınız için haberlerin çevrilmesini istediğiniz TÜM dilleri seçin:**",
        "btn_add_final": "✅ Devam Et ve Ekle",
        "connected_success": "✅ **Başarıyla Bağlandı!**\n\nInsider Finance grubunuza/kanalınıza başarıyla eklendi. Artık otomatik yayınlar alacaksınız.",
        "btn_back_main": "🔙 Ana Menüye Dön"
    },
    "zh-cn": {
        "text": (
            "📊 **关于 Insider Finance**\n\n"
            "Insider Finance 是一个机构级的金融新闻终端。我们提供实时市场新闻、突发事件更新、经济事件和重要的交易信号。\n\n"
            "此机器人专为添加到您的交易 **群组和频道** 而设计。添加后，它将自动将所有关键的市场情报直接广播给您的社区！\n\n"
            "👇 点击下方配置并将机器人添加到您的社区或加入我们的官方频道："
        ),
        "btn_group": "➕ 添加到群组",
        "btn_chan": "➕ 添加到频道",
        "btn_official": "📢 官方频道",
        "select_langs": "👇 **请选择您希望新闻为您群组/频道翻译的所有语言：**",
        "btn_add_final": "✅ 继续并添加机器人",
        "connected_success": "✅ **连接成功！**\n\nInsider Finance 已成功添加到您的群组/频道。您现在将接收自动广播。",
        "btn_back_main": "🔙 返回主菜单"
    }
}

def get_language_keyboard():
    keyboard = [
        [
            types.InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ],
        [
            types.InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es"),
            types.InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
        ],
        [
            types.InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr"),
            types.InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh-cn")
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_multi_lang_keyboard(chat_type: str, selected_langs: list, ui_lang: str, bot_username: str, msg_id: int, user_id: int):
    langs = {
        "en": "🇬🇧 English",
        "ru": "🇷🇺 Русский",
        "es": "🇪🇸 Español",
        "uz": "🇺🇿 O'zbekcha",
        "tr": "🇹🇷 Türkçe",
        "zh-cn": "🇨🇳 中文"
    }
    
    inline_kb = []
    sel_str = "-".join(selected_langs) if selected_langs else ""
    
    row = []
    for code, name in langs.items():
        text = f"✅ {name}" if code in selected_langs else name
        cb_data = f"tgl:{chat_type}:{code}:{sel_str}:{ui_lang}:{msg_id}"
        row.append(types.InlineKeyboardButton(text=text, callback_data=cb_data))
        if len(row) == 2:
            inline_kb.append(row)
            row = []
    if row:
        inline_kb.append(row)
        
    t = UI_TRANSLATIONS.get(ui_lang, UI_TRANSLATIONS["en"])
    
    if not selected_langs:
        inline_kb.append([types.InlineKeyboardButton(text="⚠️ Please select at least one language", callback_data="ignore")])
    else:
        # Pass msg_id and ui_lang so the bot can edit the private message later!
        payload = f"setup_{sel_str}_{msg_id}_{ui_lang}"
        
        # Cache for channels and groups
        PENDING_CHANNEL_SETUPS[user_id] = {
            "langs": selected_langs,
            "msg_id": msg_id,
            "ui_lang": ui_lang
        }
        
        inline_kb.append([types.InlineKeyboardButton(text="💳 Continue to Payment", callback_data=f"payopt_{chat_type}_{sel_str}_{ui_lang}")])
    
    inline_kb.append([types.InlineKeyboardButton(text="🔙 Back", callback_data=f"lang_{ui_lang}")])
    return types.InlineKeyboardMarkup(inline_keyboard=inline_kb)

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("setup_"):
        if message.chat.type == "private":
            await message.answer("Please add the bot to a group or channel to set up broadcasting.")
            return
            
        # Parse payload: setup_en-ru_50_uz
        parts = args[1].split("_")
        langs_str = parts[1]
        langs = langs_str.replace("-", ",")
        
        msg_id = None
        ui_lang = "en"
        if len(parts) >= 4:
            msg_id = parts[2]
            ui_lang = parts[3]
        
        chat_id = str(message.chat.id)
        chat_name = message.chat.title or message.chat.full_name
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Subscription).where(Subscription.group_id == chat_id))
            sub = result.scalar_one_or_none()
            from datetime import datetime, timedelta
            if sub:
                sub.target_language = langs
                sub.status = "active"
                sub.expiry_date = datetime.now() + timedelta(days=30)
            else:
                sub = Subscription(
                    group_id=chat_id,
                    group_name=chat_name,
                    is_active=True,
                    is_premium=True,
                    target_language=langs,
                    status="active",
                    expiry_date=datetime.now() + timedelta(days=30)
                )
                session.add(sub)
            await session.commit()
            
        await message.answer(f"✅ **Insider Finance Successfully Connected!**\n\nNews will be broadcasted to this channel in the following languages: **{langs.upper()}**", parse_mode="Markdown")
        
        # Now update the user's private message to show it worked!
        if msg_id and message.from_user:
            try:
                t = UI_TRANSLATIONS.get(ui_lang, UI_TRANSLATIONS["en"])
                success_text = t["connected_success"]
                btn_back = t["btn_back_main"]
                
                kb = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text=btn_back, callback_data=f"lang_{ui_lang}")]
                ])
                await bot.edit_message_text(
                    chat_id=message.from_user.id,
                    message_id=int(msg_id),
                    text=success_text,
                    reply_markup=kb,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Could not edit private message: {e}")
                
        return

    # Normal start
    await show_main_menu(message)

async def show_main_menu(message_or_callback):
    user_name = f"@{message_or_callback.from_user.username}" if message_or_callback.from_user.username else message_or_callback.from_user.first_name
    professional_message = (
        f"👋 Hello {user_name}, welcome to **Insider Finance**! 📈\n\n"
        "✨ *We deliver real-time market news, breaking updates, and trading intelligence directly to your channel, exactly when they happen.*\n\n"
        "👇 Please choose the language you understand below:"
    )
    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer(professional_message, parse_mode="Markdown", reply_markup=get_language_keyboard())
    else:
        await message_or_callback.message.edit_text(professional_message, parse_mode="Markdown", reply_markup=get_language_keyboard())

@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery):
    await show_main_menu(callback)

@dp.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[1]
    t = UI_TRANSLATIONS.get(lang_code, UI_TRANSLATIONS["en"])
    
    btn_group = types.InlineKeyboardButton(
        text=t["btn_group"], 
        callback_data=f"setup_g_{lang_code}"
    )
    btn_chan = types.InlineKeyboardButton(
        text=t["btn_chan"], 
        callback_data=f"setup_c_{lang_code}"
    )
    btn_official = types.InlineKeyboardButton(
        text=t["btn_official"], 
        url="https://t.me/InsiderFinance_org"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [btn_group, btn_chan],
        [btn_official]
    ])
    
    await callback.message.edit_text(t["text"], parse_mode="Markdown", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("setup_"))
async def setup_multi_lang(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    chat_type = parts[1]
    ui_lang = parts[2]
    msg_id = callback.message.message_id
    
    global BOT_USERNAME
    if not BOT_USERNAME:
        bot_info = await bot.get_me()
        BOT_USERNAME = bot_info.username
        
    kb = get_multi_lang_keyboard(chat_type, [ui_lang], ui_lang, BOT_USERNAME, msg_id, callback.from_user.id)
    t = UI_TRANSLATIONS.get(ui_lang, UI_TRANSLATIONS["en"])
    await callback.message.edit_text(t["select_langs"], parse_mode="Markdown", reply_markup=kb)

@dp.callback_query(F.data.startswith("tgl:"))
async def toggle_lang(callback: types.CallbackQuery):
    # data: tgl:g:en:ru-uz:uz:1234
    parts = callback.data.split(":")
    chat_type = parts[1]
    clicked_lang = parts[2]
    sel_str = parts[3]
    ui_lang = parts[4]
    msg_id = int(parts[5])
    
    selected_langs = sel_str.split("-") if sel_str else []
    
    if clicked_lang in selected_langs:
        selected_langs.remove(clicked_lang)
    else:
        selected_langs.append(clicked_lang)
        
    global BOT_USERNAME
    if not BOT_USERNAME:
        bot_info = await bot.get_me()
        BOT_USERNAME = bot_info.username
        
    kb = get_multi_lang_keyboard(chat_type, selected_langs, ui_lang, BOT_USERNAME, msg_id, callback.from_user.id)
    t = UI_TRANSLATIONS.get(ui_lang, UI_TRANSLATIONS["en"])
    await callback.message.edit_text(t["select_langs"], parse_mode="Markdown", reply_markup=kb)

@dp.callback_query(F.data == "ignore")
async def ignore_callback(callback: types.CallbackQuery):
    await callback.answer("Please select at least one language.", show_alert=True)

@dp.callback_query(F.data.startswith("payopt_"))
async def show_payment_options(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    chat_type = parts[1]
    sel_str = parts[2]
    ui_lang = parts[3]
    
    msg = "💰 **Subscription Checkout**\n\nPlan: Monthly Access ($30/mo)\nFeatures: Real-time News, Multi-language Translation.\n\nPlease select your payment method:"
    
    btn_ton = types.InlineKeyboardButton(text="💎 Pay with TON", callback_data=f"payproc_{chat_type}_{sel_str}_{ui_lang}_ton")
    btn_uzcard = types.InlineKeyboardButton(text="💳 Pay with Uzcard/Humo", callback_data=f"payproc_{chat_type}_{sel_str}_{ui_lang}_uzcard")
    btn_back = types.InlineKeyboardButton(text="🔙 Back", callback_data=f"tgl:{chat_type}:none:{sel_str}:{ui_lang}:{callback.message.message_id}")
    
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[btn_ton], [btn_uzcard], [btn_back]])
    await callback.message.edit_text(msg, parse_mode="Markdown", reply_markup=kb)

import random
from shared import PENDING_HUMO_PAYMENTS

@dp.callback_query(F.data.startswith("payproc_"))
async def process_payment(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    chat_type = parts[1]
    sel_str = parts[2]
    ui_lang = parts[3]
    method = parts[4]
    msg_id = callback.message.message_id
    user_id = callback.from_user.id
    
    global BOT_USERNAME
    if not BOT_USERNAME:
        bot_info = await bot.get_me()
        BOT_USERNAME = bot_info.username
        
    payload = f"setup_{sel_str}_{msg_id}_{ui_lang}"
    
    if chat_type == 'g':
        add_url = f"https://t.me/{BOT_USERNAME}?startgroup={payload}"
    else:
        add_url = f"https://t.me/{BOT_USERNAME}?startchannel={payload}&admin=post_messages"
        
    if method == "uzcard":
        # Generate a unique price like 30,123 UZS
        unique_amount = 30000 + random.randint(1, 999)
        
        # Save to memory
        PENDING_HUMO_PAYMENTS[unique_amount] = {
            "chat_type": chat_type,
            "sel_str": sel_str,
            "ui_lang": ui_lang,
            "msg_id": msg_id,
            "user_id": user_id,
            "add_url": add_url
        }
        
        msg = (
            f"💳 **Uzcard / Humo Payment**\n\n"
            f"Please transfer EXACTLY **{unique_amount:,} UZS** to the following card:\n\n"
            f"💳 Card Number: `8600 1234 5678 9012`\n"
            f"👤 Name: `A. Xalimov`\n\n"
            f"⚠️ *Important: You must transfer the exact amount down to the last tiyin for our system to verify it automatically.*\n\n"
            f"⏳ Waiting for payment... (The system will automatically detect when the money arrives and send you the link.)"
        )
        btn_back = types.InlineKeyboardButton(text="🔙 Back", callback_data=f"lang_{ui_lang}")
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[btn_back]])
        await callback.message.edit_text(msg, parse_mode="Markdown", reply_markup=kb)
    else:
        # Placeholder for TON payment
        msg = f"✅ **Payment Successful!** ({method.upper()})\n\nYour subscription is now active for 1 month. Click the button below to add Insider Finance to your group or channel."
        btn_add = types.InlineKeyboardButton(text="➕ Add to Group/Channel", url=add_url)
        btn_back = types.InlineKeyboardButton(text="🔙 Back to Main", callback_data=f"lang_{ui_lang}")
        
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[btn_add], [btn_back]])
        await callback.message.edit_text(msg, parse_mode="Markdown", reply_markup=kb)

@dp.message(Command("subscribe"))
async def subscribe_group(message: types.Message):
    if message.chat.type != "private":
        await message.answer("⚠️ This group is not authorized. Admin, please message me privately (@InsiderFinance_bot) to purchase a subscription and activate news for this group.")
        return
    await message.answer("Please select your preferred language to verify or activate your subscription:", reply_markup=get_language_keyboard())

@dp.message(Command("setlang"))
async def set_language(message: types.Message):
    if message.chat.type != "private":
        await message.answer("⚠️ Admin, please message me privately (@InsiderFinance_bot) to configure this group.")
        return
    await message.answer("Please select your new broadcast language:", reply_markup=get_language_keyboard())

@dp.message(Command("crash"))
async def crash_test(message: types.Message):
    print("CRASH INITIATED BY USER")
    import os, signal
    os.kill(os.getpid(), signal.SIGINT)

from datetime import datetime, timedelta

@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR))
async def channel_added(event: ChatMemberUpdated):
    if event.chat.type != "channel":
        # Group manual add
        if event.from_user.id not in PENDING_CHANNEL_SETUPS:
            await bot.send_message(event.chat.id, "⚠️ This group is not authorized. Admin, please message me privately (@InsiderFinance_bot) to purchase a subscription and activate news for this group.")
            # We can optionally leave the group here: await bot.leave_chat(event.chat.id)
        return
        
    user_id = event.from_user.id
    if user_id in PENDING_CHANNEL_SETUPS:
        setup = PENDING_CHANNEL_SETUPS.pop(user_id)
        langs = setup["langs"]
        ui_lang = setup["ui_lang"]
        msg_id = setup["msg_id"]
        
        chat_id = str(event.chat.id)
        chat_name = event.chat.title or "Channel"
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Subscription).where(Subscription.group_id == chat_id))
            sub = result.scalar_one_or_none()
            if sub:
                sub.target_language = ",".join(langs)
                sub.status = "active"
                sub.expiry_date = datetime.now() + timedelta(days=30)
            else:
                sub = Subscription(
                    group_id=chat_id,
                    group_name=chat_name,
                    is_active=True,
                    is_premium=True,
                    target_language=",".join(langs),
                    status="active",
                    expiry_date=datetime.now() + timedelta(days=30)
                )
                session.add(sub)
            await session.commit()
            
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=f"✅ **Insider Finance Successfully Connected!**\n\nNews will be broadcasted to this channel in the following languages: **{','.join(langs).upper()}**",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Could not send welcome message to channel: {e}")
            
        try:
            t = UI_TRANSLATIONS.get(ui_lang, UI_TRANSLATIONS["en"])
            success_text = t["connected_success"]
            btn_back = t["btn_back_main"]
            
            kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text=btn_back, callback_data=f"lang_{ui_lang}")]
            ])
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=int(msg_id),
                text=success_text,
                reply_markup=kb,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Could not edit private message for channel: {e}")
    else:
        # Sneaky channel manual add
        await bot.send_message(event.chat.id, "⚠️ This channel is not authorized. Admin, please message me privately (@InsiderFinance_bot) to purchase a subscription.")
