import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.environ.get("TOKEN", "TOKENNI_BU_YERGA_QOY")
ADMIN_ID = 6517211604

bot = telebot.TeleBot(TOKEN)
animelar = {}
foydalanuvchilar = set()

@bot.message_handler(commands=['start'])
def start(message):
    foydalanuvchilar.add(message.chat.id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Animelar", callback_data="list"))
    markup.add(InlineKeyboardButton("Qidirish", callback_data="search"))
    if message.from_user.id == ADMIN_ID:
        markup.add(InlineKeyboardButton("Anime qoshish", callback_data="add"))
    bot.send_message(message.chat.id, "Anime Botiga Xush Kelibsiz!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "add")
def add_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.send_message(call.message.chat.id, "Ruxsat yoq!")
        return
    bot.send_message(call.message.chat.id, "Anime nomini yozing:")
    bot.register_next_step_handler(call.message, get_anime_name)

def get_anime_name(message):
    name = message.text
    bot.send_message(message.chat.id, "Video yuboring:")
    bot.register_next_step_handler(message, get_anime_video, name)

def get_anime_video(message, name):
    if message.video or message.document:
        file_id = message.video.file_id if message.video else message.document.file_id
        animelar[name.lower()] = file_id
        bot.send_message(message.chat.id, name + " qoshildi!")
        for user_id in foydalanuvchilar:
            try:
                bot.send_message(user_id, "Yangi anime qoshildi: " + name)
            except:
                pass
    else:
        bot.send_message(message.chat.id, "Video yuboring!")

@bot.callback_query_handler(func=lambda call: call.data == "list")
def show_list(call):
    foydalanuvchilar.add(call.message.chat.id)
    if not animelar:
        bot.send_message(call.message.chat.id, "Anime yoq!")
        return
    markup = InlineKeyboardMarkup()
    for name in animelar:
        markup.add(InlineKeyboardButton(name, callback_data="anime_" + name))
    bot.send_message(call.message.chat.id, "Animelar:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("anime_"))
def send_anime(call):
    name = call.data.replace("anime_", "")
    if name in animelar:
        bot.send_video(call.message.chat.id, animelar[name], caption=name)
    else:
        bot.send_message(call.message.chat.id, "Topilmadi!")

@bot.callback_query_handler(func=lambda call: call.data == "search")
def search_prompt(call):
    bot.send_message(call.message.chat.id, "Anime nomini yozing:")
    bot.register_next_step_handler(call.message, search_anime)

def search_anime(message):
    query = message.text.lower()
    if query in animelar:
        bot.send_video(message.chat.id, animelar[query], caption=query)
    else:
        bot.send_message(message.chat.id, "Topilmadi!")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(message.chat.id, "/start yozing")

bot.polling(none_stop=True)
