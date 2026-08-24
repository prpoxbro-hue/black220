import os
import json
import asyncio
import logging
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
VERIFIED_FILE = "verified_users.json"

def get_all_users():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return {}

def save_user_to_file(user):
    try:
        users = get_all_users()
        user_id_str = str(user.id)
        if user_id_str not in users:
            users[user_id_str] = {
                'id': user.id,
                'first_name': user.first_name,
                'username': user.username
            }
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving user: {e}")

# ভেরিফাইড ইউজার ডাটাবেস হ্যান্ডলার
def get_verified_users():
    if not os.path.exists(VERIFIED_FILE):
        return {"player_ids": [], "telegram_ids": []}
    try:
        with open(VERIFIED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading verified users: {e}")
        return {"player_ids": [], "telegram_ids": []}

def save_verified_user(player_id=None, telegram_id=None):
    try:
        data = get_verified_users()
        if player_id and str(player_id) not in data["player_ids"]:
            data["player_ids"].append(str(player_id))
        if telegram_id and str(telegram_id) not in data["telegram_ids"]:
            data["telegram_ids"].append(str(telegram_id))
            
        with open(VERIFIED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving verified user: {e}")

# ================= ওয়েব সার্ভার (রেন্ডার ও মেলবেট পোস্টব্যাকের জন্য) =================
app = Flask(__name__)

@app.route('/')
def home():
    return "Melbet Bot Server is Online & Running!", 200

# মেলবেট পোস্টব্যাক রিসিভার এন্ডপয়েন্ট
@app.route('/postback', methods=['GET', 'POST'])
def melbet_postback():
    click_id = request.args.get('click_id')     # ইউজারের টেলিগ্রাম আইডি
    player_id = request.args.get('player_id')   # মেলবেট প্লেয়ার আইডি

    if click_id or player_id:
        save_verified_user(player_id=player_id, telegram_id=click_id)
        logger.info(f"✅ পোস্টব্যাক রিসিভ হয়েছে -> Telegram ID: {click_id}, Player ID: {player_id}")
        return "SUCCESS", 200
        
    return "Missing Parameters", 400

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ================= কনফিগারেশন =================
BOT_TOKEN = "8765522545:AAESdqy4SIffyqQ_doCP5hVqQ0G1EkL3ryg"
ADMIN_ID = 8650748971

# চ্যানেল লিস্ট
REQUIRED_CHANNELS = [
    {"id": "-1004333073371", "link": "https://t.me/+ORzqsgt85SRhZjU0", "name": "📢 Join Channel 1"}
]

MELBET_PROMO = "BETBD666"  # আপনার মেলবেট প্রোমো কোড
# আপনার মেলবেটের মেইন অ্যাফিলিয়েট লিংকটি এখানে বসাবেন
AFFILIATE_BASE_URL = "https://melbet.com"  
ADMIN_USER_LINK = "https://t.me/SUNNY_BRO1"

# শুধুমাত্র Apple Hack ওয়েব অ্যাপ লিঙ্ক
APPLE_HACK_URL = "https://1xbet-melbet-apple.unaux.com/"

# ইমেজ লিঙ্ক সমূহ
IMG_START = "https://i.ibb.co/LzJF0GGz/file-00000000ee647208a867f87bc931da8c.png"
IMG_LANG = "https://i.ibb.co/LzJF0GGz/file-00000000ee647208a867f87bc931da8c.png"
IMG_REGISTRATION = "https://i.ibb.co/3nLpry7/file-0000000059b072089f5ecf92b19ec92b.png"
FINAL_IMAGE_URL = "https://i.ibb.co/3nLpry7/file-0000000059b072089f5ecf92b19ec92b.png"

TEXTS = {
    'en': {
        'reg_title': "🚀 MELBET REGISTRATION",
        'reg_msg': f"⚠️ <b>WARNING:</b> You must create a new account using Promo Code: <code>{MELBET_PROMO}</code>",
        'btn_reg_link': "🔗 Register Melbet",
        'btn_next': "✅ I Have Registered",
        'wait_msg': "⏳ Checking verification with Melbet server...",
        'ask_id': "📩 Send your new Melbet User ID (Player ID):",
        'error_digit': "❌ Invalid ID! Please send numeric Melbet ID.",
        'not_verified': f"❌ <b>Verification Failed!</b>\n\nYour Account/ID was not found under Promo Code: <code>{MELBET_PROMO}</code>.\n\nPlease register using our link and promo code properly.",
        'success_caption': "✅ <b>VERIFIED SUCCESSFULLY!</b>\n🆔 ID: <code>{uid}</code>\n\nEnjoy Apple Hack Access below 👇",
        'btn_apple_hack': "🍎 APPLE HACK",
        'btn_contact': "👨‍💻 Support"
    },
    'bn': {
        'reg_title': "🚀 মেলবেট (MELBET) রেজিস্ট্রেশন",
        'reg_msg': f"⚠️ <b>সতর্কতা:</b> আপনাকে অবশ্যই প্রোমো কোড: <code>{MELBET_PROMO}</code> ব্যবহার করে নতুন একাউন্ট খুলতে হবে।",
        'btn_reg_link': "🔗 মেলবেট রেজিস্ট্রেশন",
        'btn_next': "✅ রেজিস্ট্রেশন সম্পন্ন করেছি",
        'wait_msg': "⏳ মেলবেট সার্ভারে ভেরিফিকেশন চেক করা হচ্ছে...",
        'ask_id': "📩 আপনার নতুন মেলবেট আইডি (User ID) পাঠান:",
        'error_digit': "❌ ভুল আইডি! শুধুমাত্র সঠিক সংখ্যা বা মেলবেট আইডি দিন।",
        'not_verified': f"❌ <b>ভেরিফিকেশন ব্যর্থ হয়েছে!</b>\n\nআপনার একাউন্টটি আমাদের প্রোমো কোড <code>{MELBET_PROMO}</code> দিয়ে খোলা হয়নি অথবা সার্ভারে ডাটা এখনো পৌঁছায়নি।\n\nঅনুগ্রহ করে সঠিক লিংক ও প্রোমো কোড দিয়ে একাউন্ট খুলে আবার চেষ্টা করুন।",
        'success_caption': "✅ <b>ভেরিফিকেশন সফল হয়েছে!</b>\n🆔 আইডি: <code>{uid}</code>\n\nনিচের বাটন থেকে অ্যাপেল হ্যাক ব্যবহার করুন 👇",
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
            if member.status not in ['creator', 'administrator', 'member']:
                return False
        return True
    except:
        return False

async def safe_send_photo(context, chat_id, photo, caption=None, reply_markup=None):
    try:
        await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup, parse_mode='HTML')
    except:
        await context.bot.send_message(chat_id=chat_id, text=caption, reply_markup=reply_markup, parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user_to_file(user)
    context.user_data.clear()
    
    if not await check_membership(update, context):
        keyboard = []
        for channel in REQUIRED_CHANNELS:
            keyboard.append([InlineKeyboardButton(channel["name"], url=channel["link"])])
            
        keyboard.append([InlineKeyboardButton("✅ I Have Joined", callback_data='check_join_status')])
        
        await safe_send_photo(context, update.effective_chat.id, IMG_START, f"👋 Hello {user.first_name}!\nJoin all channels to use this bot.", InlineKeyboardMarkup(keyboard))
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
        await query.message.reply_text("❌ Join both channels first!")
        return CHECK_JOIN

async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'), InlineKeyboardButton("🇧🇩 বাংলা", callback_data='lang_bn')]
    ]
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
    
    # ইউজারের টেলিগ্রাম ID সহ ডাইনামিক ট্র্যাকিং লিংক তৈরি
    separator = "&" if "?" in AFFILIATE_BASE_URL else "?"
    user_tracking_link = f"{AFFILIATE_BASE_URL}{separator}click_id={update.effective_user.id}"
    
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

    # মেলবেট পোস্টব্যাক ডাটাবেজে ইউজার ভেরিফাই চেক
    verified_data = get_verified_users()
    is_verified = (uid in verified_data["player_ids"]) or (tg_user_id in verified_data["telegram_ids"])

    # যদি ভেরিফাই না থাকে
    if not is_verified:
        separator = "&" if "?" in AFFILIATE_BASE_URL else "?"
        user_tracking_link = f"{AFFILIATE_BASE_URL}{separator}click_id={tg_user_id}"
        
        retry_keyboard = [
            [InlineKeyboardButton(t['btn_reg_link'], url=user_tracking_link)],
            [InlineKeyboardButton(t['btn_contact'], url=ADMIN_USER_LINK)]
        ]
        await update.message.reply_text(t['not_verified'], reply_markup=InlineKeyboardMarkup(retry_keyboard), parse_mode='HTML')
        return WAITING_FOR_ID

    # ভেরিফিকেশন সফল হলে
    keyboard = [
        [InlineKeyboardButton(t['btn_apple_hack'], web_app=WebAppInfo(url=APPLE_HACK_URL))],
        [InlineKeyboardButton(t['btn_contact'], url=ADMIN_USER_LINK)]
    ]

    await safe_send_photo(context, update.effective_chat.id, FINAL_IMAGE_URL, t['success_caption'].format(uid=uid), InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

# ================= অ্যাডমিন সেকশন (ব্রডকাস্ট) =================

def parse_buttons(text: str):
    if not text:
        return None, None
    marker = "BUTTONS:"
    if marker in text:
        parts = text.split(marker, 1)
        clean_text = parts[0].strip()
        button_lines = parts[1].strip().split('\n')
        
        keyboard = []
        for line in button_lines:
            if '|' in line:
                btn_parts = line.split('|', 1)
                btn_name = btn_parts[0].strip()
                btn_url = btn_parts[1].strip()
                if btn_name and btn_url.startswith(('http://', 'https://')):
                    keyboard.append([InlineKeyboardButton(btn_name, url=btn_url)])
        
        if keyboard:
            return clean_text, InlineKeyboardMarkup(keyboard)
        return clean_text, None
        
    return text, None

async def send_broadcast_to_user(bot, chat_id, bc_data):
    m_type = bc_data['type']
    file_id = bc_data['file_id']
    text = bc_data['text']
    markup = bc_data['markup']
    
    if m_type == 'photo':
        await bot.send_photo(chat_id=chat_id, photo=file_id, caption=text, reply_markup=markup, parse_mode='HTML')
    elif m_type == 'video':
        await bot.send_video(chat_id=chat_id, video=file_id, caption=text, reply_markup=markup, parse_mode='HTML')
    elif m_type == 'document':
        await bot.send_document(chat_id=chat_id, document=file_id, caption=text, reply_markup=markup, parse_mode='HTML')
    else:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode='HTML')

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    users = get_all_users()
    total_users = len(users)
    
    instruction = (
        f"👑 <b>অ্যাডমিন প্যানেল</b>\n\n"
        f"👥 <b>মোট ইউজার:</b> {total_users} জন\n\n"
        f"📢 <b>ব্রডকাস্ট মেসেজ পাঠান (ফটো, টেক্সট, ভিডিও):</b>\n\n"
        f"বাটন যোগ করার নিয়ম (ঐচ্ছিক):\n"
        f"<code>BUTTONS:\nনাম | লিংক</code>"
    )
    await update.message.reply_text(instruction, parse_mode='HTML')
    return ADMIN_GET_CONTENT

async def admin_get_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    bc_data = {'type': 'text', 'file_id': None, 'text': None, 'markup': None}
    raw_text = msg.text or msg.caption or ""
    clean_text, markup = parse_buttons(raw_text)

    if msg.photo:
        bc_data['type'] = 'photo'
        bc_data['file_id'] = msg.photo[-1].file_id
        bc_data['text'] = clean_text
        bc_data['markup'] = markup
    elif msg.video:
        bc_data['type'] = 'video'
        bc_data['file_id'] = msg.video.file_id
        bc_data['text'] = clean_text
        bc_data['markup'] = markup
    elif msg.document:
        bc_data['type'] = 'document'
        bc_data['file_id'] = msg.document.file_id
        bc_data['text'] = clean_text
        bc_data['markup'] = markup
    else:
        bc_data['type'] = 'text'
        bc_data['text'] = clean_text
        bc_data['markup'] = markup

    context.user_data['bc_data'] = bc_data

    await update.message.reply_text("📥 <b>মেসেজ প্রিভিউ:</b>", parse_mode='HTML')
    
    if bc_data['type'] == 'photo':
        await update.message.reply_photo(photo=bc_data['file_id'], caption=bc_data['text'], reply_markup=bc_data['markup'], parse_mode='HTML')
    elif bc_data['type'] == 'video':
        await update.message.reply_video(video=bc_data['file_id'], caption=bc_data['text'], reply_markup=bc_data['markup'], parse_mode='HTML')
    elif bc_data['type'] == 'document':
        await update.message.reply_document(document=bc_data['file_id'], caption=bc_data['text'], reply_markup=bc_data['markup'], parse_mode='HTML')
    else:
        await update.message.reply_text(text=bc_data['text'], reply_markup=bc_data['markup'], parse_mode='HTML')

    confirm_keyboard = [
        [InlineKeyboardButton("✅ পাঠান (Send)", callback_data='bc_confirm')],
        [InlineKeyboardButton("❌ বাতিল (Cancel)", callback_data='bc_cancel')]
    ]
    await update.message.reply_text("মেসেজটি সবার কাছে পাঠাতে চান?", reply_markup=InlineKeyboardMarkup(confirm_keyboard))
    return ADMIN_CONFIRM

async def admin_broadcast_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'bc_cancel':
        await query.edit_message_text("❌ ব্রডকাস্ট বাতিল করা হয়েছে।")
        return ConversationHandler.END
        
    if query.data == 'bc_confirm':
        await query.edit_message_text("🚀 ব্রডকাস্ট পাঠানো শুরু হয়েছে...")
        users = get_all_users()
        bc_data = context.user_data.get('bc_data')
        
        success_count = 0
        fail_count = 0
        
        for uid_str in users.keys():
            try:
                await send_broadcast_to_user(context.bot, int(uid_str), bc_data)
                success_count += 1
            except Exception:
                fail_count += 1
            await asyncio.sleep(0.05)
            
        final_text = f"✅ ব্রডকাস্ট সম্পন্ন!\n\n👥 মোট: {len(users)}\nসফল: {success_count}\nব্যর্থ: {fail_count}"
        await query.message.reply_text(final_text)
        return ConversationHandler.END

# ================= রানার =================
if __name__ == '__main__':
    # ব্যাকগ্রাউন্ডে Flask ওয়েব সার্ভার চালু করা
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

    application.add_handler(user_conv)
    application.add_handler(admin_conv)
    print("Melbet Postback Bot is starting...")
    application.run_polling()
