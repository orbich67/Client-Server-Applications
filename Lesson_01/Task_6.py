import locale
from chardet import detect


f = open('Task_6.txt', 'w', encoding='utf-8')
f.write('"сетевое программирование", "сокет", "декоратор"')
f.close()

default_encoding = locale.getpreferredencoding()
print('Кодировка системы по умолчанию:', default_encoding)

with open('Task_6.txt', 'rb') as f:
    content = f.read()
encoding = detect(content)['encoding']
print('Кодировка файла: ', encoding)

with open('Task_6.txt', encoding=encoding) as f_n:
    for el_str in f_n:
        print(f'Вывод содержимого файла в {encoding}:, {el_str}')
