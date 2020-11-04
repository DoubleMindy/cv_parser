from _utilities_ import find_description_around, delete_duplicate_values, get_request
import re

from bs4 import BeautifulSoup


PHONES_KEYWORDS = r'[+7-8]{1,2}[-\s(]{0,3}[0-9]{3}[)\s-]{0,3}[0-9]{3}[-\s]{0,3}[0-9]{2}[-\s]{0,3}[0-9]{2}'


def find_phones(domain):
    """
    domain: доменное имя страницы (str)

    return: None или все телефоны на данной странице в формате телефон-описание (dict)
    """
    print("Finding phones...")
    response = get_request(domain)
    soup = BeautifulSoup(response.text, 'lxml')
    # Словарь для описания телефона
    phones_info = dict()
    phones_list = re.findall(re.compile(PHONES_KEYWORDS), response.text)

    if not phones_list:
        return

    li_list = []
    phones_list = set(phones_list)
    # Словарь для описания телефонов
    phones_info = dict()
    for phone in phones_list:
        if not phone in phones_info.keys():
            info = find_description_around(response, phone)
            phones_info[phone] = info
            if info:
                phones_info[phone] = phones_info[phone].replace(phone, '')
    return delete_duplicate_values(phones_info)
