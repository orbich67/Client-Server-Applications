import yaml


def write_to_yaml(data, file):
    with open(file, 'w') as f_n:
        yaml.dump(data, f_n, default_flow_style=False, allow_unicode = True)


if __name__ == '__main__':
    main_data = {
        'first': ['1', '2', '3'],
        'second': 123,
        'third': {
            'first': '1€',
            'second': '2$',
            'third': '3₽',
        }
    }

    write_to_yaml(main_data, 'file_task_3.yaml')

    with open('file_task_3.yaml') as f_n:
        print(f_n.read())

    with open('file_task_3.yaml') as f_n:
        f_n_content = yaml.load(f_n, Loader=yaml.FullLoader)
        if f_n_content == main_data:
            print('Данные совпадают!')
