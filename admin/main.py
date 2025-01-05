import telebot
import time
import json
from telebot import types

from common.db import get_users_info, get_users_count
from common.tg_logging import set_logger

with open('settings.json') as f:
    data = json.load(f)

TOKEN = data.get("ApiToken")
ADMIN_ID = data.get("AdminId")


bot = telebot.TeleBot(TOKEN)
LOG = set_logger(telebot.logger, TOKEN)


def log_error(message):
    LOG.error(message)


def check_admin(user_id):
    return int(user_id) == ADMIN_ID


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if not check_admin(user_id):
        bot.reply_to(message, "Вы не админ!")
        return
    reply_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    count_button = types.KeyboardButton(text='/count')
    info_button = types.KeyboardButton(text='/show_all')
    log_button = types.KeyboardButton(text='/get_logs')
    disabled_button = types.KeyboardButton(text='/show_disabled')
    reply_markup.add(log_button, disabled_button, count_button, info_button)
    bot.reply_to(message, "Вы админ!", reply_markup=reply_markup)


@bot.message_handler(commands=['show_all'])
def handle_info(message):
    user_id = message.from_user.id
    if not check_admin(user_id):
        bot.reply_to(message, "Вы не админ!")
        return
    answer = get_users_info()
    bot.send_message(user_id, answer)


@bot.message_handler(commands=['show_disabled'])
def handle_info(message):
    user_id = message.from_user.id
    if not check_admin(user_id):
        bot.reply_to(message, "Вы не админ!")
        return
    answer = get_users_info(0)
    if len(answer) == 0:
        bot.send_message(user_id, 'Таких нет')
        return
    bot.send_message(user_id, answer)


@bot.message_handler(commands=['count'])
def handle_settings(message):
    user_id = message.from_user.id
    if not check_admin(user_id):
        bot.reply_to(message, "Вы не админ!")
        return
    count = get_users_count()
    bot.send_message(chat_id=message.from_user.id, text=f'Количество пользователей: {count}')


@bot.message_handler(commands=['get_logs'])
def handle_logs(message):
    user_id = message.from_user.id
    if not check_admin(user_id):
        bot.reply_to(message, "Вы не админ!")
        return
    with open('telebot_log.txt', 'rb') as file:
        bot.send_document(user_id, file)


while True:
    try:
        bot.polling()
    except Exception as e:
        log_error(str(e))
        LOG.info('Перезапуск через минуту')
        time.sleep(60)
