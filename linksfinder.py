from _utilities_ import soup_validation
import os.path
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


def find_page_by_urls(domain, urls, soup=None):
    """ 
    domain: доменное имя (str)
    urls: список из возможных url-ов (list)
    soup: soup-объект для домена, чтобы не делать лишних запросов к серверу (Optional <soup>)

    Найти страницу по url-шаблонам

    return: None или найденная ссылка (str)
    """
    soup = soup_validation(domain, soup)
    for word in urls:
        for link in soup.find_all('a', href=True):
            link = link.get('href')
            if re.search(re.compile(word, re.I), link):
                return urljoin(domain, link)


def find_page_by_keywords(domain, keywords, soup=None):
    """ 
    domain: доменное имя (str)
    keywords: список слов, содержащих возможное название страницы (list)
    soup: soup-объект для домена, чтобы не делать лишних запросов к серверу (Optional <soup>)

    Найти страницу по словам-шаблонам

    return: None или найденная ссылка (str)
    """
    soup = soup_validation(domain, soup)
    for word in keywords:
        for link in soup.find_all('a', href=True):
            if re.search(re.compile(word, re.I), link.text):
                return urljoin(domain, link.get('href'))


# ВНИМАНИЕ!!! Далее идет тестовый функционал.
# Использовать его можно лишь в режиме разработчика и
# крайне НЕ рекомендуется это делать, если Вы таковым не являетесь

def find_all_pages(domain, url_to_search, soup=None):
    """ 
    domain: доменное имя (str)
    path_to_search: содержит относительную ссылку, с которой нужно начинать поиск (str)
    soup: soup-объект для домена, чтобы не делать лишних запросов к серверу (Optional <soup>)

    Найти все подстраницы path_to_search на странице domain
    (пример: для domain='domain.com/contacts/' и path_to_search='/contacts' функция вернет
     список ['domain.com/contacts/filial1', 'domain.com/contacts/filial2', 'domain.com/contacts/other'])

    return: None или все найденные ссылки (list)
    """
    all_links = []
    soup = soup_validation(domain, soup)

    for link in soup.find_all('a', href=True):
        link = link.get('href')
        if re.findall(re.compile(url_to_search, re.I), link):
            all_links.append(urljoin(domain, link))
    if all_links:
        return list(set(all_links))
    return 