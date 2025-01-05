import telebot
import threading
import time
import json

from datetime import datetime
from telebot import types
from telebot.apihelper import ApiTelegramException

from common.db import create_table, get_users_from_db, update_user_in_db, add_user_to_db
from common.tg_logging import set_logger
from common.user import User


class UserSkipInfo:
    def __init__(self, should_skip=1):
        self.should_skip = should_skip
        self.skipped = 0

    def can_update(self):
        return self.skipped >= self.should_skip

    def new_cycle(self):
        self.skipped = 0


with open('settings.json') as f:
    data = json.load(f)

NIGHT = data.get("night")
MORNING = data.get("morning")
MINUTES_OFFSET_DEFAULT = data.get("minutes_offset")
TOKEN = data.get("ApiToken")
user_skip_dict: [int, UserSkipInfo] = dict()


create_table()
users = get_users_from_db()

bot = telebot.TeleBot(TOKEN)


LOG = set_logger(telebot.logger, TOKEN)


def log_message(message):
    LOG.info(message)


def log_error(message):
    LOG.error(message)


def set_user_skips():
    for user in users.values():
        should_skip = user.minutes_offset // MINUTES_OFFSET_DEFAULT - 1
        user_skip_dict[user.user_id] = UserSkipInfo(should_skip)


def update_user_skip(user: User):
    should_skip = user.minutes_offset // MINUTES_OFFSET_DEFAULT - 1
    user_skip_dict[user.user_id] = UserSkipInfo(should_skip)



set_user_skips()


def send_messages():
    current_time = datetime.now().time()
    if MORNING <= current_time.hour < NIGHT:
        user_for_disable = []
        sended_users = []
        for user in users.values():
            if user.enabled != 1:
                continue
            user_skip_info: UserSkipInfo = user_skip_dict[user.user_id]
            if user_skip_info.can_update():
                try:
                    bot.send_message(user.user_id, "Выпрями спину")
                    user_skip_info.new_cycle()
                    sended_users.append(user.username)
                except ApiTelegramException as e:
                    log_error(f'{user.username}:{user.user_id} недоступен')
                    log_error(str(e))
                    if e.error_code == 400 or e.error_code == 403:
                        user_for_disable.append(user)
            else:
                user_skip_info.skipped += 1
        for user in user_for_disable:
            user.enabled = 0
            update_user_in_db(user)
        if len(sended_users) > 0:
            log_message(f'informed {sended_users}')
        if len(user_for_disable) > 0:
            log_message(f'deleted {user_for_disable}')
    else:
        log_message('Сообщение не отправлено, так как ночь')
        pass


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    log_message(f'{message.from_user.username}:{user_id}  Start using')
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    stop_button = types.KeyboardButton(text='/stop')
    settings_button = types.KeyboardButton(text='/settings')
    info_button = types.KeyboardButton(text='/info')
    reply_markup.add(stop_button, settings_button, info_button)
    if user_id not in users.keys():
        username = message.from_user.username
        new_user = User(user_id=user_id, username=username)
        users[user_id] = new_user
        update_user_skip(new_user)
        add_user_to_db(new_user)
        bot.send_message(user_id, "Теперь я буду напоминать тебе выпрямить спину с 10 до 22!\n" +
                                  "Изменить периодичность:\n/settings", reply_markup=reply_markup)
    else:
        user = users[user_id]
        if user.enabled != 1:
            user.enabled = 1
            update_user_in_db(user)
            bot.reply_to(message, "Я снова могу напоминать тебе о спине\nБольше информации - /info",
                         reply_markup=reply_markup)
        else:
            bot.reply_to(message, "Оповещения уже активны\nБольше информации:\n/info", reply_markup=reply_markup)


@bot.message_handler(commands=['info'])
def handle_info(message):
    user_id = int(message.from_user.id)
    user = users[user_id]
    if user.enabled == 1:
        bot.send_message(user_id, f'Не беспокою с {user.night} до {user.morning}\n'
                                  f'Периодичность оповещений: {user.minutes_offset} мин')
    else:
        bot.send_message(user_id, f'Оповещения отключены\nДля включения напиши\n/start')
    log_message(f'{user.username}:{user_id}  Send info')


@bot.message_handler(commands=['stop'])
def handle_info(message):
    user_id = int(message.from_user.id)
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    info_button = types.KeyboardButton(text='/info')
    start_button = types.KeyboardButton(text='/start')
    reply_markup.add(info_button, start_button)
    user = users[user_id]
    user.enabled = 0
    update_user_in_db(user)
    bot.send_message(user_id, f'Больше не буду беспокоить\nВозобновить оповещения:\n/start',
                     reply_markup=reply_markup)
    log_message(f'{user.username}:{user_id}  Stop sending')


@bot.message_handler(commands=['settings'])
def handle_settings(message):
    reply_markup = types.InlineKeyboardMarkup(row_width=2)
    offset_buttons = [types.InlineKeyboardButton(text='15 мин', callback_data='offset_15'),
                      types.InlineKeyboardButton(text='30 мин', callback_data='offset_30'),
                      types.InlineKeyboardButton(text='60 мин', callback_data='offset_60'),
                      types.InlineKeyboardButton(text='120 мин', callback_data='offset_120')]
    reply_markup.add(*offset_buttons)
    bot.send_message(chat_id=message.from_user.id, text="Выберите периодичность:", reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    callback_data = call.data
    if callback_data.startswith('offset_'):
        try:
            new_offset = int(callback_data.split('_')[1])
        except Exception as e:
            log_error(f'Ошибка колбека: {callback_data}')
            log_error(str(e))
            return
        if user_id in users:
            user = users[user_id]
            user.minutes_offset = new_offset
            update_user_in_db(user)
            update_user_skip(user)
            bot.send_message(call.from_user.id, text=f"Периодичность теперь {new_offset} мин")
            bot.answer_callback_query(call.id, text=f"Периодичность теперь {new_offset} мин")
            log_message(f'{user.username}:{user_id}  >>> Offset = {new_offset}')
        else:
            bot.answer_callback_query(call.id, text="Произошла ошибка.")
    else:
        log_error(f'Ошибка колбека: {callback_data}')


def polling_thread():
    while True:
        log_message('STARTING BOT')
        try:
            bot.polling()
        except Exception as e:
            log_error(str(e))
            log_message('Запуск через 60 секунд')
            time.sleep(60)


polling_thread = threading.Thread(target=polling_thread, name='telebot.exe', daemon=True)
polling_thread.start()

try:
    while True:
        if datetime.now().hour >= NIGHT or datetime.now().hour < MORNING:
            time.sleep(3600)  # Пауза на 1 час в ночное время
        else:
            time.sleep(60 * MINUTES_OFFSET_DEFAULT)
        send_messages()
except Exception as e:
    log_error(str(e))
    log_message('Запуск через 60 секунд')
    time.sleep(60)    
