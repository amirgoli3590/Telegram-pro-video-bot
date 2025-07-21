from telebot import types

def admin_handler(bot, message, db, save_db):
    chat_id = str(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ افزودن دسته‌بندی", "➖ حذف دسته‌بندی")
    markup.row("📂 افزودن قسمت", "🗑 حذف قسمت")
    markup.row("📋 نمایش دسته‌بندی‌ها", "🚪 خروج")
    msg = bot.send_message(chat_id, "🔧 پنل مدیریت فعال شد:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_admin_option, bot, db, save_db)

def process_admin_option(message, bot, db, save_db):
    if message.text == "➕ افزودن دسته‌بندی":
        msg = bot.send_message(message.chat.id, "نام دسته‌بندی جدید را بفرست:")
        bot.register_next_step_handler(msg, add_category, bot, db, save_db)
    elif message.text == "➖ حذف دسته‌بندی":
        msg = bot.send_message(message.chat.id, "نام دسته‌بندی برای حذف را بفرست:")
        bot.register_next_step_handler(msg, delete_category, bot, db, save_db)
    elif message.text == "📂 افزودن قسمت":
        msg = bot.send_message(message.chat.id, "نام دسته‌بندی که می‌خواهی قسمت به آن اضافه کنی را بفرست:")
        bot.register_next_step_handler(msg, add_episode, bot, db, save_db)
    elif message.text == "🗑 حذف قسمت":
        msg = bot.send_message(message.chat.id, "نام دسته‌بندی که می‌خواهی قسمت از آن حذف کنی را بفرست:")
        bot.register_next_step_handler(msg, delete_episode, bot, db, save_db)
    elif message.text == "📋 نمایش دسته‌بندی‌ها":
        show_categories(message, bot, db)
    elif message.text == "🚪 خروج":
        bot.send_message(message.chat.id, "✅ از پنل مدیریت خارج شدید.")
    else:
        bot.send_message(message.chat.id, "⚠️ دستور نامعتبر است.")
        admin_handler(bot, message, db, save_db)

def add_category(message, bot, db, save_db):
    category = message.text.strip()
    if category not in db['categories']:
        db['categories'][category] = {}
        save_db(db)
        bot.send_message(message.chat.id, f"✅ دسته‌بندی «{category}» اضافه شد.")
    else:
        bot.send_message(message.chat.id, "⚠️ این دسته‌بندی قبلاً وجود دارد.")
    admin_handler(bot, message, db, save_db)

def delete_category(message, bot, db, save_db):
    category = message.text.strip()
    if category in db['categories']:
        del db['categories'][category]
        save_db(db)
        bot.send_message(message.chat.id, f"🗑 دسته‌بندی «{category}» حذف شد.")
    else:
        bot.send_message(message.chat.id, "⚠️ این دسته‌بندی وجود ندارد.")
    admin_handler(bot, message, db, save_db)

def add_episode(message, bot, db, save_db):
    category = message.text.strip()
    if category in db['categories']:
        msg = bot.send_message(message.chat.id, "نام قسمت جدید را بفرست:")
        bot.register_next_step_handler(msg, lambda m: save_episode(m, bot, db, save_db, category))
    else:
        bot.send_message(message.chat.id, "⚠️ این دسته‌بندی وجود ندارد.")
        admin_handler(bot, message, db, save_db)

def save_episode(message, bot, db, save_db, category):
    episode_name = message.text.strip()
    msg = bot.send_message(message.chat.id, "آیدی فایل ویدیو (file_id) را بفرست:")
    bot.register_next_step_handler(msg, lambda m: save_episode_file(m, bot, db, save_db, category, episode_name))

def save_episode_file(message, bot, db, save_db, category, episode_name):
    file_id = message.text.strip()
    db['categories'][category][episode_name] = file_id
    save_db(db)
    bot.send_message(message.chat.id, f"✅ قسمت «{episode_name}» به دسته‌بندی «{category}» اضافه شد.")
    admin_handler(bot, message, db, save_db)

def delete_episode(message, bot, db, save_db):
    category = message.text.strip()
    if category in db['categories']:
        msg = bot.send_message(message.chat.id, "نام قسمتی که می‌خواهید حذف کنید را بفرست:")
        bot.register_next_step_handler(msg, lambda m: remove_episode(m, bot, db, save_db, category))
    else:
        bot.send_message(message.chat.id, "⚠️ این دسته‌بندی وجود ندارد.")
        admin_handler(bot, message, db, save_db)

def remove_episode(message, bot, db, save_db, category):
    episode_name = message.text.strip()
    if episode_name in db['categories'][category]:
        del db['categories'][category][episode_name]
        save_db(db)
        bot.send_message(message.chat.id, f"🗑 قسمت «{episode_name}» از «{category}» حذف شد.")
    else:
        bot.send_message(message.chat.id, "⚠️ این قسمت وجود ندارد.")
    admin_handler(bot, message, db, save_db)

def show_categories(message, bot, db):
    if db['categories']:
        categories_text = "\n".join([f"📂 {c}" for c in db['categories']])
    else:
        categories_text = "❌ هیچ دسته‌بندی‌ای وجود ندارد."
    bot.send_message(message.chat.id, categories_text)
