words = ['attribute', 'класс', 'функция', 'type']

for word in words:
    if not word.isascii():
        print(f'слово "{word}" невозможно записать в байтовом типе')
