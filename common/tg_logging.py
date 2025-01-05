import logging
import telebot


class MaskingFilter(logging.Filter):
    def __init__(self, token):
        super().__init__()
        self._token = token

    def filter(self, record):
        record.msg = record.msg.replace(self._token, '<API_TOKEN>')
        return True


def set_logger(logger: telebot.logger, filter_token=None):
    telebot.logger.setLevel(logging.INFO)  # Установите уровень логирования по необходимости
    handler = logging.FileHandler('telebot_log.txt', mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if filter_token is not None:
        logger.addFilter(MaskingFilter(filter_token))
    return logger
