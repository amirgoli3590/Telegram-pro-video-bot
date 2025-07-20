import telebot
import json
import datetime
import threading
import os
from admin_panel import admin_handler
from zarinpal import create_payment_link, verify_payment

# اطلاعات اصلی ربات
TOKEN = '7621509071:AAGQQFbqxI5hvJBRoYEhGvicmT9P0dJSi_U'
CHANNEL_USERNAME = '@amiramir3590'
ADMIN_ID = 7536757725
DB_FILE = 'database.json'

# بارگذاری دیتابیس
def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"users": {}, "categories": {}}, f)
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

db = load_db()

# بررسی اشتراک کاربر
def has_access(user_id):
    user = db['users'].get(str(user_id))
    if not user:
        return False
    expire_date = datetime.datetime.strptime(user['expire_date'], '%Y-%m-%d')
    return datetime.datetime.now() <= expire_date

# هشدار پایان اشتراک
def notify_expiring_users():
    while True:
        now = datetime.datetime.now()
        for uid, data in db['users'].items():
            expire_date = datetime.datetime.strptime(data['expire_date'], '%Y-%m-%d')
            if (expire_date - now).days == 1 and not data.get('notified'):
                try:
                    bot.send_message(uid, "⏳ اشتراک شما فردا منقضی می‌شود. لطفاً تمدید کنید ✅")
                    db['users'][uid]['notified'] = True
                    save_db(db)
                except:
                    continue
        threading.Event().wait(86400)

threading.Thread(target=notify_expiring_users, daemon=True).start()

# دستورات ربات
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    if uid not in db['users']:
        start_date = datetime.datetime.now()
        expire_date = start_date + datetime.timedelta(days=7)
        db['users'][uid] = {
            "username": message.from_user.username,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "expire_date": expire_date.strftime('%Y-%m-%d'),
            "is_premium": False,
            "notified": False
        }
        save_db(db)
        bot.send_message(uid, "🎉 خوش آمدید! ۷ روز دسترسی رایگان دارید.")
    else:
        bot.send_message(uid, "👋 خوش آمدید. از منو انتخاب کنید:")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📂 دسته‌بندی‌ها", "🛒 خرید اشتراک")
    bot.send_message(uid, "از منو انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🛒 خرید اشتراک")
def buy_subscription(message):
    uid = str(message.chat.id)
    link, authority = create_payment_link(uid)
    db['users'][uid]['payment_authority'] = authority
    save_db(db)
    bot.send_message(uid, f"💳 برای خرید اشتراک روی لینک زیر بزنید:\n{link}")

@bot.message_handler(func=lambda m: m.text == "📂 دسته‌بندی‌ها")
def show_categories(message):
    uid = str(message.chat.id)
    if not has_access(uid):
        bot.send_message(uid, "⛔ اشتراک شما منقضی شده. لطفاً تمدید کنید.")
        return
    if not db['categories']:
        bot.send_message(uid, "📂 هنوز هیچ دسته‌بندی‌ای اضافه نشده.")
        return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in db['categories']:
        markup.row(category)
    markup.row("🔙 بازگشت")
    bot.send_message(uid, "📂 یک دسته‌بندی انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in db['categories'].keys())
def show_episodes(message):
    uid = str(message.chat.id)
    category = message.text
    episodes = db['categories'][category]
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for ep in episodes:
        markup.row(ep)
    markup.row("🔙 بازگشت")
    bot.send_message(uid, f"🎬 قسمت‌های {category}:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in [ep for eps in db['categories'].values() for ep in eps])
def send_video(message):
    uid = str(message.chat.id)
    if not has_access(uid):
        bot.send_message(uid, "⛔ اشتراک شما منقضی شده.")
        return
    for category, episodes in db['categories'].items():
        if message.text in episodes:
            file_id = episodes[message.text]
            msg = bot.send_video(uid, file_id)
            threading.Timer(30, lambda: bot.delete_message(uid, msg.message_id)).start()
            break

@bot.message_handler(func=lambda m: m.text == "🔙 بازگشت")
def back(message):
    start(message)

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.chat.id == ADMIN_ID:
        admin_handler(bot, message, db, save_db)
    else:
        bot.send_message(message.chat.id, "⚠️ شما دسترسی به پنل مدیریت ندارید.")

print("🤖 ربات آنلاین است...")
bot.infinity_polling()
