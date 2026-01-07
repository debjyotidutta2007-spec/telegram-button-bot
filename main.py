from telebot import TeleBot, types

# ================= CONFIG =================
BOT_TOKEN = "8249947917:AAEhVRrlVZK0bukQcERDf4T7Y40GD2Wz2Lo"

CHANNEL_ID = None            # এখন channel ব্যবহার না করলে None রাখো
GROUP_ID = -1003090825117   # তোমার group id

bot = TeleBot(BOT_TOKEN)
user_state = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🛠 Post Builder Bot\n\n"
        "Use /createpost to create a new post"
    )

# ================= CREATE POST =================
@bot.message_handler(commands=['createpost'])
def create_post(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("📷 Photo", "🎥 Video", "📁 File")

    bot.send_message(
        message.chat.id,
        "What do you want to post?",
        reply_markup=kb
    )

    user_state[message.chat.id] = {"step": "choose_type"}

# ================= TYPE SELECT =================
@bot.message_handler(func=lambda m: m.text in ["📷 Photo", "🎥 Video", "📁 File"])
def choose_type(message):
    chat_id = message.chat.id
    if chat_id not in user_state:
        return

    user_state[chat_id]["type"] = message.text
    user_state[chat_id]["step"] = "wait_media"

    bot.send_message(
        chat_id,
        "Now send the media with caption",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ================= MEDIA RECEIVE =================
@bot.message_handler(content_types=['photo', 'video', 'document'])
def receive_media(message):
    chat_id = message.chat.id
    if chat_id not in user_state or user_state[chat_id]["step"] != "wait_media":
        return

    user_state[chat_id]["media"] = message
    user_state[chat_id]["caption"] = message.caption or ""
    user_state[chat_id]["step"] = "wait_buttons"

    bot.send_message(
        chat_id,
        "Send the link(s) in the format:\n\n"
        "[Button text + link]\n\n"
        "Example:\n"
        "[480p + https://example.com]\n\n"
        "Multiple buttons in one row:\n"
        "[480p + link] [720p + link]\n\n"
        "Multiple rows:\n"
        "[480p + link]\n"
        "[720p + link]"
    )

# ================= BUTTON PARSER =================
@bot.message_handler(func=lambda m: "[" in m.text and "+" in m.text)
def parse_buttons(message):
    chat_id = message.chat.id
    if chat_id not in user_state or user_state[chat_id]["step"] != "wait_buttons":
        return

    markup = types.InlineKeyboardMarkup()
    lines = message.text.strip().split("\n")

    for line in lines:
        row = []
        parts = line.split("]")
        for part in parts:
            if "[" in part and "+" in part:
                text, link = part.replace("[", "").split("+", 1)
                row.append(
                    types.InlineKeyboardButton(
                        text.strip(),
                        url=link.strip()
                    )
                )
        if row:
            markup.add(*row)

    user_state[chat_id]["markup"] = markup
    user_state[chat_id]["step"] = "confirm"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("▶️ Ready", "❌ Cancel")

    bot.send_message(
        chat_id,
        "Approximate view of the post is ready.\n"
        "If everything is correct, click ▶️ Ready\n"
        "If you want to change buttons, send them again.",
        reply_markup=kb
    )

# ================= CANCEL =================
@bot.message_handler(func=lambda m: m.text == "❌ Cancel")
def cancel_post(message):
    user_state.pop(message.chat.id, None)
    bot.send_message(
        message.chat.id,
        "❌ Post cancelled",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ================= PUBLISH =================
@bot.message_handler(func=lambda m: m.text == "▶️ Ready")
def publish_post(message):
    chat_id = message.chat.id
    data = user_state.get(chat_id)
    if not data:
        return

    media = data["media"]
    caption = data["caption"]
    markup = data["markup"]

    def send(chat):
        if media.photo:
            bot.send_photo(chat, media.photo[-1].file_id,
                           caption=caption, reply_markup=markup)
        elif media.video:
            bot.send_video(chat, media.video.file_id,
                           caption=caption, reply_markup=markup)
        elif media.document:
            bot.send_document(chat, media.document.file_id,
                              caption=caption, reply_markup=markup)

    if GROUP_ID:
        send(GROUP_ID)

    if CHANNEL_ID:
        send(CHANNEL_ID)

    bot.send_message(
        chat_id,
        "✅ Your post is ready!",
        reply_markup=types.ReplyKeyboardRemove()
    )

    user_state.pop(chat_id, None)

# ================= RUN =================
print("Bot is running...")
bot.infinity_polling()
