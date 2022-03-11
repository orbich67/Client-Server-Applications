"""Программа-клиент"""

from common.utils import get_message, send_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    DEFAULT_PORT, ERROR, DEFAULT_IP_ADDRESS, SENDER, MESSAGE, MESSAGE_TEXT
from errors import ReqFieldMissingError, ServerError
from decos import log
import sys
import json
import socket
import time
import argparse
import logging
import logs.config_client_log
sys.path.append('../')


# Инициализация клиентского логгера
CLIENT_LOGGER = logging.getLogger('client')
# сформировать presence-сообщение


@log
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


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной команды"""
    message = input('Введите сообщение для отправки или \'quit\' для завершения работы: ')
    if message == 'quit':
        sock.close()
        CLIENT_LOGGER.info(f'Завершение работы по команде "{message}" пользователя {account_name}.')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


@log
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                           f'{message[SENDER]}: "{message[MESSAGE_TEXT]}"')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


# обработать ответ сервера
@log
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


@log
def arg_parser():
    """Парсер аргументов командной строки,
    читает и возвращает 3 параметра (server_address, server_port, client_mode)"""
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # проверка номера порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
            f' В качестве порта может быть указано число в диапазоне от 1024 до 65535')
        sys.exit(1)

    # проверка допустимого режима работы клиента
    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
                               f'допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    """Загружаем параметры командной строки"""
    server_address, server_port, client_mode = arg_parser()

    CLIENT_LOGGER.info(
        f'Запущен клиент с параметрами: '
        f'адрес сервера: {server_address}, порт: {server_port}, режим работы: {client_mode}.')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence())
        answer = process_ans(get_message(transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Принят ответ: {answer}')
        print(f'Соединение с сервером установлено.')

    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        # если соединение с сервером установлено корректно,
        # начинаем обмен, согласно требуемому режиму.
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            # режим работы - отправка сообщений
            if client_mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)
            # режим работы - прием сообщений
            if client_mode == 'listen':
                try:
                    message_from_server(get_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
