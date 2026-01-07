from telebot import TeleBot, types

BOT_TOKEN = "7922370408:AAE28OdF8UP-M8TtS4sdMackOIX3fu2Y2_E"

bot = TeleBot(BOT_TOKEN)

DATA = {
    "channel_id": None,
    "group_id": None
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome\n\n"
        "Commands:\n"
        "/setchannel – Set Channel ID\n"
        "/setgroup – Set Group ID\n"
        "/post – Create button post"
    )

@bot.message_handler(commands=['setchannel'])
def set_channel(message):
    bot.send_message(message.chat.id, "📢 Send Channel ID:")
    bot.register_next_step_handler(message, save_channel)

def save_channel(message):
    try:
        DATA["channel_id"] = int(message.text)
        bot.send_message(message.chat.id, "✅ Channel ID saved")
    except:
        bot.send_message(message.chat.id, "❌ Invalid Channel ID")

@bot.message_handler(commands=['setgroup'])
def set_group(message):
    bot.send_message(message.chat.id, "👥 Send Group ID:")
    bot.register_next_step_handler(message, save_group)

def save_group(message):
    try:
        DATA["group_id"] = int(message.text)
        bot.send_message(message.chat.id, "✅ Group ID saved")
    except:
        bot.send_message(message.chat.id, "❌ Invalid Group ID")

@bot.message_handler(commands=['post'])
def ask_link(message):
    if not DATA["channel_id"] or not DATA["group_id"]:
        bot.send_message(
            message.chat.id,
            "⚠️ Set Channel & Group first\n"
            "Use /setchannel and /setgroup"
        )
        return

    bot.send_message(message.chat.id, "🔗 Send the link:")
    bot.register_next_step_handler(message, create_post)

def create_post(message):
    link = message.text

    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🎬 Download Now", url=link)
    markup.add(btn)

    caption = (
        "🎥 New Movie Uploaded\n\n"
        "⬇️ Click below to download"
    )

    bot.send_message(DATA["channel_id"], caption, reply_markup=markup)
    bot.send_message(DATA["group_id"], caption, reply_markup=markup)

    bot.send_message(message.chat.id, "✅ Posted Successfully")

bot.infinity_polling()
