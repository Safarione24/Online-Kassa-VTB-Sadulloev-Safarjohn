import json

data = [
    {'id': 1, 'name': 'Садуллоев.С.М', 'balance': 4500},
    {'id': 2, 'name': 'Мусин.Д.Н', 'balance': 8700.20},
    {'id': 3, 'name': 'Шабакаев.Р.Р', 'balance': 90123},
    {'id': 4, 'name': 'Маркелов.Н.А', 'balance': -93},
    {'id': 5, 'name': 'Агоян.А.Г', 'balance': 76000},
    {'id': 6, 'name': 'Джонсон.М.И', 'balance': 64840000000},
    {'id': 7, 'name': 'Джордан.М.Д', 'balance': 100000000000},
    {'id': 8, 'name': 'Рикардо.М.М', 'balance': 900123},
    {'id': 9, 'name': 'Грег.Д.П', 'balance': 19999},
    {'id': 10, 'name': 'Бедняков.Ж.Р', 'balance': -10000}
]

with open("data.json", "w", encoding='utf-8') as f:
    f.write(json.dumps(data, indent=2, ensure_ascii=False))
