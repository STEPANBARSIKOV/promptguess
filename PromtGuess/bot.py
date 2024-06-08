import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from logic import *
from config import *
import random

bot = telebot.TeleBot(API_TOKEN)

api = Text2ImageAPI('https://api-key.fusionbrain.ai/', API_KEY, SECRET_KEY)
gpt_api = OpenAIAPI(GPT_KEY)
model_id = api.get_model()

user_sessions = {}

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я сгенерирую изображение и предложу вам угадать, на основе какого промта оно создано.")
    generate_and_send_image(message.chat.id)

def generate_and_send_image(chat_id):
    initial_prompt = "Generate 4 creative image prompts"
    prompts = gpt_api.generate_prompts(initial_prompt)
    correct_prompt = random.choice(prompts)
    
    uuid = api.generate(correct_prompt, model_id)
    images = api.check_generation(uuid)[0]
    path = f'{chat_id}.png'
    api.convert_to_img(images, path)
    
    photo = open(path, 'rb')
    
    markup = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(text=prompt, callback_data=prompt) for prompt in prompts]
    random.shuffle(buttons)
    for button in buttons:
        markup.add(button)
    
    bot.send_photo(chat_id, photo, reply_markup=markup)
    user_sessions[chat_id] = correct_prompt

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    correct_prompt = user_sessions.get(call.message.chat.id)
    if call.data == correct_prompt:
        bot.send_message(call.message.chat.id, "Правильно!")
    else:
        bot.send_message(call.message.chat.id, f"Неправильно! Правильный промт был: {correct_prompt}")
    
    # Сгенерировать и отправить новое изображение
    generate_and_send_image(call.message.chat.id)

bot.infinity_polling()
