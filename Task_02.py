import json


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json') as f_n:
        dict_to_json = json.load(f_n)
        dict_to_json['orders'].append({
            'item': item,
            'quantity': quantity,
            'price': price,
            'buyer': buyer,
            'date': date,
        })
    with open('orders.json', 'w') as f_w:
        json.dump(dict_to_json, f_w, indent=4)


if __name__ == '__main__':
    write_order_to_json('Intel Core 2 Duo E8600', 1, 1072.59, 'Pavel', '07.12.2017')
    write_order_to_json('Intel Core 2 Quad Q9650', 1, 3187.01, 'Alex', '16.04.2018')
    write_order_to_json('Intel Xeon E3-1226V3', 1, 3557.30, 'Daria', '01.11.2021')
    write_order_to_json('Intel Xeon E3-1270V3', 1, 3826.61, 'Sergey', '22.01.2022')
