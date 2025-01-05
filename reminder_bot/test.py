# import telebot
# from telebot.apihelper import ApiTelegramException
import sqlite3


def migrate_user_from_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("ALTER TABLE users ADD COLUMN enabled INTEGER DEFAULT 1;")
    conn.commit()
    conn.close()

migrate_user_from_db()

# Создаем бота
# bot = telebot.TeleBot('Token')
# 
# 
# def send_buttons(message):
#     bot.send_message(message.chat.id, 'Выберите одну из кнопок:')
# 
# try:
#     bot.send_message('id', 'Выберите одну из кнопок:')
# except ApiTelegramException as e:
#     print(e.error_code == 403)
