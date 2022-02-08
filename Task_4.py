words = ['разработка', 'администрирование', 'protocol', 'standard']

for word in words:
    word_bytes = word.encode("utf-8")
    word_str = word_bytes.decode("utf-8")
    print(f'{word} => {word_bytes} => {word_str}, {word == word_str}')
