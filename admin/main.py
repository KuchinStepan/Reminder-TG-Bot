import telebot
import sqlite3
import logging
import time
import json
from telebot import types

from common.db import get_users_info

with open('settings.json') as f:
    data = json.load(f)

TOKEN = data.get("ApiToken")


bot = telebot.TeleBot(TOKEN)


def set_logger():
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)  # Установите уровень логирования по необходимости
    handler = logging.FileHandler('admin_logs.txt', mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


LOG = set_logger()


def log_error(message):
    LOG.error(message)


def get_users_count():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE enabled = 1")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def check_admin(user_id):
    return int(user_id) == 1684300554


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
