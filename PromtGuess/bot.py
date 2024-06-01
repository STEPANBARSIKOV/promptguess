import telebot
from logic import *
from config import *


bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hello")
    

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message (message) :
    prompt = message.text
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', API_KEY, SECRET_KEY)
    model_id =api.get_model()
    uuid = api.generate(prompt, model_id)
    images = api.check_generation(uuid) [0]
    path = f'{message.from_user.id}.png'
    api. convert_to_img (images, path)
    photo = open(path, 'rb')
    bot.send_photo(message.chat.id, photo)


bot.infinity_polling()