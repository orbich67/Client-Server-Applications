"""Программа-сервер"""

import socket
import sys
from common.utils import *
from common.variables import *

def process_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESSES: 400,
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
        print(f'TCP-порт: {listen_port}')
        if listen_port < 1204 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535')
        sys.exit(1)

    # присваиваем IP-адрес для прослушивания (по умолчанию слушает все доступные адреса)
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
            print(f'IP-адрес для прослушивания: {listen_address}')
        else:
            listen_address = ''
            print(f'IP-адрес для прослушивания: все доступные')
    except IndexError:
        print('После параметра \'a\' необходимо указать адрес, который будет слушать сервер')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            print(f'Получен запрос на соединение от клиента с адресом и портом: {client_address}')
            print(message_from_client)
            response = process_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print(f'Получено некорректное сообщение от клиента с адресом и портом {client_address}')
            client.close()


if __name__ == '__main__':
    main()
