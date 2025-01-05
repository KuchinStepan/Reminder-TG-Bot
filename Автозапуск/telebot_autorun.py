import time
import psutil
import logging
import subprocess


ADMIN = 'telebot_admin.exe'
BOT = 'telebot.exe'
MINUTES_OFFSET = 60 * 12  # 10 часов


def set_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('autorun_logs.txt', mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


LOG = set_logger()

try:
    while True:
        LOG.info('~Проверка состояний~')
        is_admin_running = False
        is_telebot_running = False
        for proc in psutil.process_iter():
            name = proc.name()
            if name == BOT:
                is_telebot_running = True
            if name == ADMIN:
                is_admin_running = True

        if not is_telebot_running:
            LOG.info('Запуск основного бота')
            subprocess.Popen([BOT])

        time.sleep(3)

        if not is_admin_running:
            LOG.info('Запуск админки')
            subprocess.Popen([ADMIN])

        time.sleep(60 * MINUTES_OFFSET)
except Exception as e:
    LOG.error(str(e))
