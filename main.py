from telebot import TeleBot, types

BOT_TOKEN = "7922370408:AAE28OdF8UP-M8TtS4sdMackOIX3fu2Y2_E"

CHANNEL_ID = -1001234567890
GROUP_ID   = -1003090825117

bot = TeleBot(BOT_TOKEN)

user_state = {}

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🛠 Post Builder Bot\n\n"
        "Use /createpost to create a new post"
    )

# ---------- CREATE POST ----------
@bot.message_handler(commands=['createpost'])
def create_post(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("📷 Photo", "🎥 Video", "📁 File")

    bot.send_message(
        message.chat.id,
        "What do you want to post?",
        reply_markup=keyboard
    )
    user_state[message.chat.id] = {"step": "choose_type"}

# ---------- TYPE SELECT ----------
@bot.message_handler(func=lambda m: m.text in ["📷 Photo", "🎥 Video", "📁 File"])
def choose_type(message):
    chat_id = message.chat.id
    user_state[chat_id]["type"] = message.text

    bot.send_message(
        chat_id,
        "Now send the file",
        reply_markup=types.ReplyKeyboardRemove()
    )
    user_state[chat_id]["step"] = "wait_media"

# ---------- MEDIA RECEIVE ----------
@bot.message_handler(content_types=['photo', 'video', 'document'])
def receive_media(message):
    chat_id = message.chat.id
    if chat_id not in user_state or user_state[chat_id]["step"] != "wait_media":
        return

    user_state[chat_id]["media"] = message
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

# ---------- BUTTON PARSE ----------
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
                row.append(types.InlineKeyboardButton(text.strip(), url=link.strip()))
        if row:
            markup.add(*row)

    user_state[chat_id]["markup"] = markup
    user_state[chat_id]["step"] = "confirm"

    bot.send_message(
        chat_id,
        "Approximate view of the post is ready.\n"
        "If everything is correct, click ▶️ Ready",
        reply_markup=types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        ).add("▶️ Ready")
    )

# ---------- READY ----------
@bot.message_handler(func=lambda m: m.text == "▶️ Ready")
def publish_post(message):
    chat_id = message.chat.id
    data = user_state.get(chat_id)

    if not data:
        return

    media = data["media"]
    markup = data["markup"]

    caption = "🎬 New Post\n\n⬇️ Select option:"

    def send(chat):
        if media.photo:
            bot.send_photo(chat, media.photo[-1].file_id, caption=caption, reply_markup=markup)
        elif media.video:
            bot.send_video(chat, media.video.file_id, caption=caption, reply_markup=markup)
        elif media.document:
            bot.send_document(chat, media.document.file_id, caption=caption, reply_markup=markup)

    send(CHANNEL_ID)
    send(GROUP_ID)

    bot.send_message(chat_id, "✅ Your post is ready!")
    user_state.pop(chat_id, None)

# ---------- RUN ----------
bot.infinity_polling()
