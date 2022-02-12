str_1 = 'разработка'
str_2 = 'сокет'
str_3 = 'декоратор'

str_1u = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
str_2u = '\u0441\u043e\u043a\u0435\u0442'
str_3u = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'

print(f'"{str_1}", тип {type(str_1)}, "{str_1u}", тип {type(str_1u)}, {str_1 == str_1u}')
print(f'"{str_2}", тип {type(str_2)}, "{str_2u}", тип {type(str_2u)}, {str_2 == str_2u}')
print(f'"{str_3}", тип {type(str_3)}, "{str_3u}", тип {type(str_3u)}, {str_3 == str_3u}')
