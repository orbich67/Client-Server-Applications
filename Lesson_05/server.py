"""Программа-сервер"""

import socket
import sys
import json
import logging
import logs.config_server_log
from common.utils import get_message, send_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    DEFAULT_PORT, MAX_CONNECTIONS, ERROR

# Инициализация клиентского логгера
SERVER_LOGGER = logging.getLogger('server')


def process_client_message(message):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
    проверяет корректность, возвращает словарь-ответ для клиента.
    :param message:
    :return:
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def main():
    # присваиваем TCP-порт для работы (по умолчанию использует 7777)
    # ---параметры командной строки скрипта server.py -p <port> -a <addr>---
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if not 1023 < listen_port < 65536:
            raise ValueError
    except IndexError:
        SERVER_LOGGER.critical(f'Попытка запуска сервера без номера порта.'
                               f' После параметра -\'p\' необходимо указать номер.')
        sys.exit(1)
    except ValueError:
        SERVER_LOGGER.critical(
            f'Попытка запуска сервера с неподходящим номером порта: {listen_port}.'
            f' В качестве порта может быть указано число в диапазоне от 1024 до 65535')
        sys.exit(1)

    # присваиваем IP-адрес для прослушивания (по умолчанию слушает все доступные адреса)
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        SERVER_LOGGER.critical(f'Попытка запуска сервера без IP-адреса для прослушивания.'
                               f' После параметра \'a\' необходимо указать адрес, который будет слушать сервер')

    print(f'Сервер запущен. Адрес: {listen_address} (по умолчанию все доступные адреса), порт: {listen_port}.')
    SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}'
                       f' (по умолчанию соединения принимаются с любых адресов).')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        SERVER_LOGGER.info(f'Установлено соединение с адресом и портом: {client_address}')
        try:
            message_from_client = get_message(client)
            SERVER_LOGGER.debug(f'Получено сообщение {message_from_client}')
            # print(f'Получен запрос на соединение от клиента с адресом и портом: {client_address}')
            # print(message_from_client)
            response = process_client_message(message_from_client)
            SERVER_LOGGER.info(f'Cформирован и отправлен ответ {response} клиенту с адресом {client_address}')
            send_message(client, response)
            SERVER_LOGGER.debug(f'Соединение с клиентом {client_address} закрывается.')
            client.close()
        except (ValueError, json.JSONDecodeError):
            SERVER_LOGGER.error(f'От клиента {client_address} получено некорректное сообщение.'
                                f' Соединение закрывается.')
            client.close()


if __name__ == '__main__':
    main()
