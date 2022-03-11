"""Программа-сервер"""

import socket
import sys
import argparse
import json
import logging
import select
import time
import logs.config_server_log
from common.utils import get_message, send_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    DEFAULT_PORT, MAX_CONNECTIONS, ERROR, MESSAGE, MESSAGE_TEXT, SENDER

sys.path.append('../')
from decos import log

# Инициализация серверного логгера
SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(message, messages_list, client):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
    проверяет корректность, возвращает словарь-ответ для клиента.
    :param message:
    :param messages_list:
    :param client:
    :return:
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    # Если получено сообщение о присутствии - принимаем и отвечаем.
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    # Если получено сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    # Иначе Bad request
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


@log
def arg_parser():
    """Парсер аргументов командной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверка получения корректного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(
            f'Попытка запуска сервера с неподходящим номером порта: {listen_port}.'
            f' В качестве порта должно быть указано число в диапазоне от 1024 до 65535')
        sys.exit(1)

    return listen_address, listen_port


def main():
    """Загрузка параметров командной строки, если нет параметров - устанавливаются значения по умолчанию"""
    listen_address, listen_port = arg_parser()

    SERVER_LOGGER.info(
        f'Запущен сервер, порт для подключений: {listen_port}, '
        f'адрес с которого принимаются подключения: {listen_address}'
        f' (по умолчанию соединения принимаются с любых адресов).')
    print(f'Сервер запущен. Адрес: {listen_address} (по умолчанию все доступные адреса), порт: {listen_port}.')

    # готовим сокет.
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    # таймаут для операций с сокетом
    transport.settimeout(0.2)

    # список клиентов, очередь сообщений
    clients, messages = [], []

    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            # проверка подключений
            client, client_address = transport.accept()
        except OSError as err:
            # timeout вышел
            print(err.errno)
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соединение с адресом и портом: {client_address}')
            clients.append(client)

        read_data_lst = []
        write_data_lst = []
        err_lst = []

        # Проверяем наличие событий ввода-вывода
        try:
            if clients:
                read_data_lst, write_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
        if read_data_lst:
            for client_with_message in read_data_lst:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message)
                except:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                       f'отключился от сервера.')
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and write_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in write_data_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    SERVER_LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    waiting_client.close()
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
