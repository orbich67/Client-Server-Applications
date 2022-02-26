"""Программа-клиент"""

import sys
import json
import socket
import time
import logging
import logs.config_client_log
from common.utils import get_message, send_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    DEFAULT_PORT, ERROR, DEFAULT_IP_ADDRESS


# Инициализация клиентского логгера
CLIENT_LOGGER = logging.getLogger('client')


# сформировать presence-сообщение
def create_presence(account_name='Guest'):
    """
    Функция генерирует запрос о присутствии клиента
    :param account_name:
    :return:
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано "{PRESENCE}" сообщение для пользователя "{account_name}"')
    return out


# обработать ответ сервера
def process_ans(message):
    """
    Функция разбирает ответ сервера
    :param message:
    :return:
    """
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    raise ValueError


def main():
    # ---параметры командной строки скрипта client.py <addr> [<port>]---
    try:
        # проверка номера порта
        server_address = sys.argv[1]
        server_port = int(sys.argv[2][1:-1])
        if not 1023 < server_port < 65536:
            raise ValueError
        CLIENT_LOGGER.info(f'Запущен клиент с параметрами: '
                           f'адрес сервера: {server_address}, порт: {server_port}')
    except IndexError:
        # если не пришли аргументы - устанавливаем адрес и порт по умолчанию
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
        CLIENT_LOGGER.info(f'Запущен клиент с параметрами: '
                           f'адрес сервера: {server_address}, порт: {server_port}')
    except ValueError:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
            f' В качестве порта может быть указано число в диапазоне от 1024 до 65535')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = create_presence()
    send_message(transport, message_to_server)
    try:
        answer = process_ans(get_message(transport))
        CLIENT_LOGGER.info(f'Принят ответ от сервера {answer}')
        print(answer)
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json-строку.')


if __name__ == '__main__':
    main()
