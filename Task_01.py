import csv
import re
from chardet import detect


def get_data(lst_files):
    os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []
    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]

    for file in lst_files:
        with open(file, 'rb') as f_n:
            content = f_n.read()
        encoding = detect(content)['encoding']

        with open(file, encoding=encoding) as f_n:
            for row in f_n:
                row = row.rstrip()
                if re.match('Изготовитель ОС', row):
                    os_prod_list.append(re.search(r'(Изготовитель ОС).\s*(.*)', row).group(2))
                elif re.match('Название ОС', row):
                    os_name_list.append(re.search(r'(Название ОС).\s*(.*)', row).group(2))
                elif re.match('Код продукта', row):
                    os_code_list.append(re.search(r'(Код продукта).\s*(.*)', row).group(2))
                elif re.match('Тип системы', row):
                    os_type_list.append(re.search(r'(Тип системы).\s*(.*)', row).group(2))

    for idx in range(len(lst_files)):
        main_data.append([
            os_prod_list[idx],
            os_name_list[idx],
            os_code_list[idx],
            os_type_list[idx]
         ])
    return main_data


def write_to_csv(file, data):
    with open(file, 'w') as f_n:
        f_n_writer = csv.writer(f_n)
        data = get_data(data)
        for row in data:
            f_n_writer.writerow(row)


if __name__ == "__main__":
    write_to_csv('file_task_1.csv', ['info_1.txt', 'info_2.txt', 'info_3.txt'])
