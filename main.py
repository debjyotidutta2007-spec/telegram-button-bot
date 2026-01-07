from telebot import TeleBot, types

# -------- CONFIG --------
BOT_TOKEN = "7922370408:AAE28OdF8UP-M8TtS4sdMackOIX3fu2Y2_E"

CHANNEL_ID = -100XXXXXXXXXX   # Your Channel ID
GROUP_ID   = -1003090825117   # Your Group ID
# ------------------------

bot = TeleBot(BOT_TOKEN)
user_state = {}

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🛠 Post Builder Bot\n\n"
        "Commands:\n"
        "/createpost – Create a new post"
    )

# ---------- CREATE POST ----------
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

# ---------- POST TYPE ----------
@bot.message_handler(func=lambda m: m.text in ["📷 Photo", "🎥 Video", "📁 File"])
def choose_type(message):
    chat_id = message.chat.id

    if chat_id not in user_state:
        return

    user_state[chat_id]["type"] = message.text
    user_state[chat_id]["step"] = "wait_media"

    bot.send_message(
        chat_id,
        "📤 Now send the media",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ---------- MEDIA ----------
@bot.message_handler(content_types=['photo', 'video', 'document'])
def receive_media(message):
    chat_id = message.chat.id

    if chat_id not in user_state or user_state[chat_id]["step"] != "wait_media":
        return

    user_state[chat_id]["media"] = message

    # If caption already sent with media
    if message.caption:
        user_state[chat_id]["caption"] = message.caption
        user_state[chat_id]["step"] = "wait_buttons"

        bot.send_message(
            chat_id,
            "🔘 Caption received.\n\n"
            "Send the button links in this format:\n\n"
            "[Button text + link]\n\n"
            "Example:\n"
            "[Download 480p + https://example.com]\n\n"
            "Same row:\n"
            "[480p + link] [720p + link]\n\n"
            "New rows:\n"
            "[480p + link]\n"
            "[720p + link]"
        )

    # If no caption with media
    else:
        user_state[chat_id]["step"] = "wait_caption"
        bot.send_message(chat_
