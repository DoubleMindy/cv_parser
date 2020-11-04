from _utilities_ import tag_visible, get_request, list_without_unions
import re

from bs4 import BeautifulSoup


ADDRESSES = ['г. ', 'улица', 'ул. ', 'проезд', ' пр.', 'пр.-т', ' д.']
# Исключаем тексты, содержащие информацию о проезде к адресу
STOP_WORDS = ['такси', 'автобус', 'маршрутка', 'трамвай', 'ост.', 'до остановки']

# Применение данных выражений имеет слишком большую вычислительную сложность,
# поэтому было решено отказаться от них:
# ADDRESS_KEYWORDS_STREET = r'.*[А-Я].*[\n]{0,1}.*(ул){1}(ица){0,1}[\.\s]+[А-Я].*'
# ADDRESS_KEYWORDS_PROSPECT = r'.*(г){0,1}(гор){0,1}(ород){0,1}[\.\s]+[А-Я].*[\n]{0,1}.*(пр){1}(оспект){0,1}[\.\s]+[А-Я].*'


def find_address(domain):
    """
    domain: доменное имя страницы (str)

    return: все реальные адреса на данной странице (list)
    """
    print("Finding addresses...")
    addresses_list = []
    response = get_request(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = soup.findAll(text=True)
    # Из всех текстов оставляем только те, что видны на странице
    visible_texts = filter(tag_visible, texts) 

    for text in visible_texts:
        for word in ADDRESSES:
            text = ' '.join(text.split()).replace('\n', '')
            # Исключаем тексты, содержащие выражения вида "2020г." и слова, заканчивающиеся на "г."
            if text.find(word) > -1 and not re.search(re.compile(r'[\d]+г'), text) \
            and not re.search(re.compile(r'[а-яА-Яa-zA-Z]+г'), text):
                addresses_list.append(text)

    addresses_list = list_without_unions(set(addresses_list))
    bad_addresses = []
    for word in STOP_WORDS:
        for addr in addresses_list:
            if addr.find(word) > -1:
                bad_addresses.append(addr)

    # Исключаем адреса, содержащие стоп-слова
    return [item for item in addresses_list if item not in bad_addresses]