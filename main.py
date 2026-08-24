import os
import json
import asyncio
import logging
import requests
from threading import Thread
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

# ================= লগিং সেটআপ =================
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= ফাইল ডাটাবেস =================
DATA_FILE = "users.json"
VERIFIED_FILE = "verified_melbet.json"

def get_all_users():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_user_to_file(user):
    try:
        users = get_all_users()
        user_id_str = str(user.id)
        if user_id_str not in users:
            users[user_id_str] = {'id': user.id, 'first_name': user.first_name, 'username': user.username}
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=4, ensure_ascii=False)
    except: pass

def get_verified_data():
    if not os.path.exists(VERIFIED_FILE): return {"player_ids": [], "telegram_ids": []}
    try:
        with open(VERIFIED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {"player_ids": [], "telegram_ids": []}

def add_verified_data(player_id=None, telegram_id=None):
    try:
        data = get_verified_data()
        updated = False
        if player_id and str(player_id) not in data["player_ids"]:
            data["player_ids"].append(str(player_id))
            updated = True
        if telegram_id and str(telegram_id) not in data["telegram_ids"]:
            data["telegram_ids"].append(str(telegram_id))
            updated = True
            
        if updated:
            with open(VERIFIED_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error: {e}")

# ================= কনফিগারেশন =================
BOT_TOKEN = "8765522545:AAESdqy4SIffyqQ_doCP5hVqQ0G1EkL3ryg"
ADMIN_ID = 8650748971

REQUIRED_CHANNELS = [
    {"id": "-1004333073371", "link": "https://t.me/+ORzqsgt85SRhZjU0", "name": "📢 Join Channel 1"}
]

MELBET_PROMO = "BLACK220"

# স্ক্রিনশটের ২ নম্বর লিংকটি (Link ID: 4459528) এখানে পেস্ট করবেন
AFFILIATE_BASE_URL = "https://refpa3665.com/L?tag=d_3468223m_45415c_&site=3468223&ad=45415&r=registration"  

ADMIN_USER_LINK = "https://t.me/SUNNY_BRO1"
APPLE_HACK_URL = "https://1xbet-melbet-apple.unaux.com/"

IMG_START = "https://i.ibb.co/LzJF0GGz/file-00000000ee647208a867f87bc931da8c.png"
IMG_LANG = "https://i.ibb.co/LzJF0GGz/file-00000000ee647208a867f87bc931da8c.png"
IMG_REGISTRATION = "https://i.ibb.co/3nLpry7/file-0000000059b072089f5ecf92b19ec92b.png"
FINAL_IMAGE_URL = "https://i.ibb.co/3nLpry7/file-0000000059b072089f5ecf92b19ec92b.png"

# ================= ওয়েব সার্ভার =================
app = Flask(__name__)

@app.route('/')
def home():
    return "Melbet Postback Server Active!", 200

@app.route('/postback', methods=['GET', 'POST'])
def melbet_postback():
    click_id = request.args.get('click_id') or request.args.get('subid') or request.args.get('sub1') or request.args.get('sub_id')
    player_id = request.args.get('player_id') or request.args.get('user_id') or request.args.get('player')

    if click_id or player_id:
        add_verified_data(player_id=player_id, telegram_id=click_id)
        logger.info(f"🔥 POSTBACK RECEIVED -> Telegram ID: {click_id}, Player ID: {player_id}")
        
        try:
            admin_msg = (
                f"🔔 <b>নতুন রেজিস্ট্রেশন কনফার্ম হয়েছে!</b>\n\n"
                f"🆔 <b>Player ID:</b> <code>{player_id}</code>\n"
                f"👤 <b>Telegram ID:</b> <code>{click_id}</code>\n"
                f"🎁 <b>Promo:</b> {MELBET_PROMO}"
            )
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
                "chat_id": ADMIN_ID,
                "text": admin_msg,
                "parse_mode": "HTML"
            }, timeout=5)
        except Exception as e:
            logger.error(f"Error: {e}")

        return "SUCCESS", 200
        
    return "No Data", 400

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ================= বটের টেক্সট =================
TEXTS = {
    'en': {
        'reg_title': "🚀 MELBET REGISTRATION",
        'reg_msg': f"⚠️ <b>WARNING:</b> You must create a new account using our link and Promo Code: <code>{MELBET_PROMO}</code>",
        'btn_reg_link': "🔗 Register Melbet",
        'btn_next': "✅ I Have Registered",
        'wait_msg': "⏳ Checking Postback records with Melbet server...",
        'ask_id': "📩 Send your new Melbet User ID (Player ID):",
        'error_digit': "❌ Invalid ID! Send numeric Melbet ID.",
        'not_verified': f"❌ <b>VERIFICATION FAILED!</b>\n\nYour Melbet ID was <b>NOT FOUND</b> under Promo Code: <code>{MELBET_PROMO}</code>.\n\n⚠️ You must register through our official button above. Please wait 2-3 minutes for server sync and try again.",
        'success_caption': "✅ <b>VERIFIED BY POSTBACK!</b>\n🆔 Melbet ID: <code>{uid}</code>\n🎁 Promo: <code>{promo}</code> (Confirmed)\n\nEnjoy Apple Hack Access below 👇",
        'btn_apple_hack': "🍎 APPLE HACK",
        'btn_contact': "👨‍💻 Support"
    },
    'bn': {
        'reg_title': "🚀 মেলবেট (MELBET) রেজিস্ট্রেশন",
        'reg_msg': f"⚠️ <b>সতর্কতা:</b> আপনাকে অবশ্যই আমাদের লিংক ও প্রোমো কোড: <code>{MELBET_PROMO}</code> ব্যবহার করে নতুন একাউন্ট খুলতে হবে।",
        'btn_reg_link': "🔗 মেলবেট রেজিস্ট্রেশন",
        'btn_next': "✅ রেজিস্ট্রেশন সম্পন্ন করেছি",
        'wait_msg': "⏳ মেলবেট পোস্টব্যাক সার্ভারে আইডি চেক করা হচ্ছে...",
        'ask_id': "📩 আপনার নতুন মেলবেট আইডি (Player ID) পাঠান:",
        'error_digit': "❌ ভুল ফরম্যাট! শুধুমাত্র সঠিক সংখ্যা বা আইডিটি দিন।",
        'not_verified': f"❌ <b>ভেরিফিকেশন ব্যর্থ হয়েছে!</b>\n\nআপনার মেলবেট আইডিটি আমাদের প্রোমো কোড <code>{MELBET_PROMO}</code> এর অধীনে পাওয়া যায়নি!\n\n⚠️ আপনাকে অবশ্যই উপরের বাটনে ক্লিক করে একাউন্ট খুলতে হবে। মাত্র একাউন্ট করে থাকলে ২-৩ মিনিট অপেক্ষা করে আবার আইডিটি পাঠান।",
        'success_caption': "✅ <b>পোস্টব্যাক ভেরিফিকেশন সফল হয়েছে!</b>\n🆔 মেলবেট আইডি: <code>{uid}</code>\n🎁 প্রোমো কোড: <code>{promo}</code> (নিশ্চিত)\n\nনিচের বাটন থেকে অ্যাপেল হ্যাক ব্যবহার করুন 👇",
        'btn_apple_hack': "🍎 অ্যাপেল হ্যাক",
        'btn_contact': "👨‍💻 এডমিন সাপোর্ট"
    }
}

CHECK_JOIN, SELECT_LANGUAGE, SHOW_MELBET, WAITING_FOR_ID = range(4)
ADMIN_GET_CONTENT, ADMIN_CONFIRM = range(10, 12)

# ================= হ্যান্ডলার ফাংশনস =================
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        for channel in REQUIRED_CHANNELS:
            member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=update.effective_user.id)
            if member.status not in ['creator', 'administrator', 'member']: return False
        return True
    except: return False

async def safe_send_photo(context, chat_id, photo, caption=None, reply_markup=None):
    try: await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup, parse_mode='HTML')
    except: await context.bot.send_message(chat_id=chat_id, text=caption, reply_markup=reply_markup, parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user_to_file(user)
    context.user_data.clear()
    
    if not await check_membership(update, context):
        keyboard = [[InlineKeyboardButton(c["name"], url=c["link"])] for c in REQUIRED_CHANNELS]
        keyboard.append([InlineKeyboardButton("✅ I Have Joined", callback_data='check_join_status')])
        await safe_send_photo(context, update.effective_chat.id, IMG_START, f"👋 Hello {user.first_name}!\nJoin channel to use this bot.", InlineKeyboardMarkup(keyboard))
        return CHECK_JOIN
        
    await show_language_menu(update, context)
    return SELECT_LANGUAGE

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await check_membership(update, context):
        await show_language_menu(update, context)
        return SELECT_LANGUAGE
    else:
        await query.message.reply_text("❌ Join channel first!")
        return CHECK_JOIN

async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'), InlineKeyboardButton("🇧🇩 বাংলা", callback_data='lang_bn')]]
    if update.callback_query:
        try: await update.callback_query.message.delete()
        except: pass
    await safe_send_photo(context, update.effective_chat.id, IMG_LANG, "🌐 Select Language:", InlineKeyboardMarkup(keyboard))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang
    t = TEXTS[lang]
    
    uid = update.effective_user.id
    # সব ধরণের ট্র্যাকিং প্যারামিটার পাঠানো হচ্ছে
    user_tracking_link = f"{AFFILIATE_BASE_URL}&click_id={uid}&subid={uid}&sub1={uid}"
    
    keyboard = [
        [InlineKeyboardButton(t['btn_reg_link'], url=user_tracking_link)],
        [InlineKeyboardButton(t['btn_next'], callback_data='account_created')]
    ]
    
    text = f"{t['reg_title']}\n\n{t['reg_msg']}"
    try: await query.message.delete()
    except: pass
    await safe_send_photo(context, update.effective_chat.id, IMG_REGISTRATION, text, InlineKeyboardMarkup(keyboard))
    return SHOW_MELBET

async def wait_and_ask_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'bn')
    await query.message.reply_text(TEXTS[lang]['ask_id'], parse_mode='HTML')
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    tg_user_id = str(update.effective_user.id)
    lang = context.user_data.get('lang', 'bn')
    t = TEXTS[lang]
    
    if not uid.isdigit() or len(uid) < 6:
        await update.message.reply_text(t['error_digit'])
        return WAITING_FOR_ID

    msg = await update.message.reply_text(t['wait_msg'], parse_mode='HTML')
    await asyncio.sleep(2)
    try: await msg.delete()
    except: pass

    verified_data = get_verified_data()
    is_verified = (uid in verified_data["player_ids"]) or (tg_user_id in verified_data["telegram_ids"])

    if not is_verified:
        user_tracking_link = f"{AFFILIATE_BASE_URL}&click_id={tg_user_id}&subid={tg_user_id}&sub1={tg_user_id}"
        retry_keyboard = [
            [InlineKeyboardButton(t['btn_reg_link'], url=user_tracking_link)],
            [InlineKeyboardButton(t['btn_contact'], url=ADMIN_USER_LINK)]
        ]
        await update.message.reply_text(t['not_verified'], reply_markup=InlineKeyboardMarkup(retry_keyboard), parse_mode='HTML')
        return WAITING_FOR_ID

    keyboard = [
        [InlineKeyboardButton(t['btn_apple_hack'], web_app=WebAppInfo(url=APPLE_HACK_URL))],
        [InlineKeyboardButton(t['btn_contact'], url=ADMIN_USER_LINK)]
    ]
    caption_text = t['success_caption'].format(uid=uid, promo=MELBET_PROMO)
    await safe_send_photo(context, update.effective_chat.id, FINAL_IMAGE_URL, caption_text, InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

# ================= অ্যাডমিন পাওয়ার ও ম্যানুয়াল ভেরিফাই কমান্ড =================
async def admin_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("ব্যবহার নিয়ম: `/add 1779905627`", parse_mode='Markdown')
        return
    player_id = context.args[0].strip()
    add_verified_data(player_id=player_id)
    await update.message.reply_text(f"✅ Player ID: `{player_id}` ম্যানুয়ালি ভেরিফাইড করা হয়েছে!", parse_mode='Markdown')

# ================= ব্রডকাস্ট সেকশন =================
def parse_buttons(text: str):
    if not text: return None, None
    marker = "BUTTONS:"
    if marker in text:
        parts = text.split(marker, 1)
        clean_text = parts[0].strip()
        button_lines = parts[1].strip().split('\n')
        keyboard = []
        for line in button_lines:
            if '|' in line:
                btn_parts = line.split('|', 1)
                b_name, b_url = btn_parts[0].strip(), btn_parts[1].strip()
                if b_name and b_url.startswith(('http://', 'https://')):
                    keyboard.append([InlineKeyboardButton(b_name, url=b_url)])
        if keyboard: return clean_text, InlineKeyboardMarkup(keyboard)
        return clean_text, None
    return text, None

async def send_broadcast_to_user(bot, chat_id, bc_data):
    m_type, file_id, text, markup = bc_data['type'], bc_data['file_id'], bc_data['text'], bc_data['markup']
    if m_type == 'photo': await bot.send_photo(chat_id=chat_id, photo=file_id, caption=text, reply_markup=markup, parse_mode='HTML')
    elif m_type == 'video': await bot.send_video(chat_id=chat_id, video=file_id, caption=text, reply_markup=markup, parse_mode='HTML')
    elif m_type == 'document': await bot.send_document(chat_id=chat_id, document=file_id, caption=text, reply_markup=markup, parse_mode='HTML')
    else: await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode='HTML')

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users = get_all_users()
    instruction = (
        f"👑 <b>অ্যাডমিন প্যানেল</b>\n\n"
        f"👥 <b>মোট ইউজার:</b> {len(users)} জন\n\n"
        f"🛠 <b>ম্যানুয়াল ভেরিফাই কমান্ড:</b>\n"
        f"<code>/add মেলবেট_আইডি</code> (যেমন: <code>/add 1779905627</code>)\n\n"
        f"📢 ব্রডকাস্ট পাঠাতে মেসেজ (ফটো/ভিডিও/টেক্সট) পাঠান।"
    )
    await update.message.reply_text(instruction, parse_mode='HTML')
    return ADMIN_GET_CONTENT

async def admin_get_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    bc_data = {'type': 'text', 'file_id': None, 'text': None, 'markup': None}
    raw_text = msg.text or msg.caption or ""
    clean_text, markup = parse_buttons(raw_text)

    if msg.photo: bc_data.update({'type': 'photo', 'file_id': msg.photo[-1].file_id, 'text': clean_text, 'markup': markup})
    elif msg.video: bc_data.update({'type': 'video', 'file_id': msg.video.file_id, 'text': clean_text, 'markup': markup})
    elif msg.document: bc_data.update({'type': 'document', 'file_id': msg.document.file_id, 'text': clean_text, 'markup': markup})
    else: bc_data.update({'type': 'text', 'text': clean_text, 'markup': markup})

    context.user_data['bc_data'] = bc_data
    confirm_keyboard = [[InlineKeyboardButton("✅ পাঠান", callback_data='bc_confirm'), InlineKeyboardButton("❌ বাতিল", callback_data='bc_cancel')]]
    await update.message.reply_text("মেসেজটি সবার কাছে পাঠাতে চান?", reply_markup=InlineKeyboardMarkup(confirm_keyboard))
    return ADMIN_CONFIRM

async def admin_broadcast_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'bc_confirm':
        await query.edit_message_text("🚀 ব্রডকাস্ট পাঠানো শুরু হয়েছে...")
        users = get_all_users()
        bc_data = context.user_data.get('bc_data')
        s, f = 0, 0
        for uid_str in users.keys():
            try:
                await send_broadcast_to_user(context.bot, int(uid_str), bc_data)
                s += 1
            except: f += 1
            await asyncio.sleep(0.05)
        await query.message.reply_text(f"✅ সম্পন্ন!\nমোট: {len(users)}, সফল: {s}, ব্যর্থ: {f}")
    else:
        await query.edit_message_text("❌ বাতিল করা হয়েছে।")
    return ConversationHandler.END

# ================= রানার =================
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    user_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHECK_JOIN: [CallbackQueryHandler(check_join_callback, pattern='^check_join_status$')],
            SELECT_LANGUAGE: [CallbackQueryHandler(set_language, pattern='^lang_')],
            SHOW_MELBET: [CallbackQueryHandler(wait_and_ask_id, pattern='^account_created$')],
            WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)],
        },
        fallbacks=[CommandHandler('start', start)],
        allow_reentry=True
    )

    admin_conv = ConversationHandler(
        entry_points=[CommandHandler('admin', admin_start)],
        states={
            ADMIN_GET_CONTENT: [MessageHandler(filters.ALL & ~filters.COMMAND, admin_get_content)],
            ADMIN_CONFIRM: [CallbackQueryHandler(admin_broadcast_action, pattern='^bc_')]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(CommandHandler('add', admin_add_id))
    application.add_handler(user_conv)
    application.add_handler(admin_conv)
    print("Bot Running...")
    application.run_polling()
