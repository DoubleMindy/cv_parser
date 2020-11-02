import requests
import re

from bs4 import BeautifulSoup
from bs4.element import Comment


ADDRESSES = ['г. ', 'улица', 'ул. ', 'проезд', ' пр.', 'пр.-т', ' д.']

# These expressions have too large complexity so I used non-regular list to find address
# ADDRESS_KEYWORDS_STREET = r'.*[А-Я].*[\n]{0,1}.*(ул){1}(ица){0,1}[\.\s]+[А-Я].*'
# ADDRESS_KEYWORDS_PROSPECT = r'.*(г){0,1}(гор){0,1}(ород){0,1}[\.\s]+[А-Я].*[\n]{0,1}.*(пр){1}(оспект){0,1}[\.\s]+[А-Я].*'


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def list_without_unions(l):
    uniq = []
    for i, elem_i in enumerate(l):
        for j, elem_j in enumerate(l):
            if elem_i in elem_j and i != j:
                uniq.append(elem_i)
    return [item for item in l if item not in uniq]


def find_address(domain):
    print("Finding addresses...")
    addresses_list = []
    stop_words = ['такси', 'автобус', 'маршрутка', 'трамвай']
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts) 

    for t in visible_texts:
        for word in ADDRESSES:
            t = ' '.join(t.split()).replace('\n', '')
            if t.find(word) > -1 and not re.search(re.compile(r'[\d]+г'), t) \
            and not re.search(re.compile(r'[а-яА-Яa-zA-Z]+г'), t) and re.search(re.compile(r'[\d]+'), t):
                addresses_list.append(t)

    addresses_info = list_without_unions(set(addresses_list))
    bad_addresses = []
    for word in stop_words:
        for addr in addresses_info:
            if addr.find(word) > -1:
                bad_addresses.append(addr)
    return [item for item in addresses_info if item not in bad_addresses]