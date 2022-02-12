import subprocess
import chardet
import platform


param = '-n' if platform.system().lower() == 'windows' else '-c'
source = [['ping', param, '4', 'yandex.ru'], ['ping', param, '4', 'youtube.com']]

for args in source:
    result = subprocess.Popen(args, stdout=subprocess.PIPE)

    for line in result.stdout:
        result = chardet.detect(line)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'))
