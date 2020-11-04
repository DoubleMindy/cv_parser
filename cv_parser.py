from dispatcher import parse

import argparse
import errno
import pprint
import json
import os, os.path

__author__ = "2da271c296d29175019208ef5227a22f"
__copyright__ = "2020, October"

parser = argparse.ArgumentParser(description='Универсальный парсер Интернет-сайтов')
parser.add_argument('link', type=str, help='Сайт, который хотим парсить')
parser.add_argument('-p', '--path', type=str, help='Полный путь, куда выгрузим результат')
parser.add_argument('-t', '--test', action='store_true', help='Режим разработчика')
args = parser.parse_args()

if args.test:
    result = parse(args.link, deep_test=True)
elif args.link:
    result = parse(args.link)

if not args.path:
    path = 'result.json'
else:
    path = args.path
    if path[-5:] != '.json':
    	path += '/result.json'
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

with open(path, "w") as write_file:
    json.dump(result, write_file, indent=4, ensure_ascii=False)

print('JSON-файл успешно создан, полный путь: {}'.format(os.path.abspath(path)))
pprint.pprint(result, indent=4, width=100)