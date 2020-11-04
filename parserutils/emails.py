from _utilities_ import find_description_around, get_request
import re

from bs4 import BeautifulSoup

EMAILS_KEYWORDS = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}'


def find_emails(domain):    
    """
    domain: доменное имя страницы (str)

    return: все почтовые адреса на данной странице в формате адрес-описание (dict)
    """
    print("Finding emails...")
    response = get_request(domain)
    soup = BeautifulSoup(response.text, 'lxml')
    # Получение всех почтовых адресов по регулярному выражению
    emails_list = re.findall(re.compile(EMAILS_KEYWORDS), response.text)

    if not emails_list:
        return
    # Сохранение порядка почтовых адресов со страницы
    # (предполагаем, что "основная" почта указана сначала) 
    emails_list = sorted(set(emails_list), key=emails_list.index)
    
    # Словарь для описания почты
    emails_info = dict()
    for email in emails_list:
        if not email in emails_info.keys():
            emails_info[email] = find_description_around(response, email)
                       
    return emails_info