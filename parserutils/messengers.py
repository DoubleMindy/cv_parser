from _utilities_ import get_request
from bs4 import BeautifulSoup


MESSENGERS_KEYWORDS = ['whatsapp', 'viber', 'tele.click', 'wa.me', 'telegram', 'icq', 'vk.me', 'skype']


def find_messengers(domain):
    """
    domain: доменное имя страницы (str)

    return: все мессенджеры на данной странице в формате название-ссылка (dict)
    """
    print("Finding messengers...")
    messengers_links = dict()
    response = get_request(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = soup.find_all('a', href=True)
    for word in MESSENGERS_KEYWORDS:
        for link in all_links:
            href_tag = link.get('href')
            if href_tag.find(word) > -1:
                # Обработка ссылки вида telegram:bot=company_bot 
                # (неявный редирект на @company_bot)
                if href_tag.find('=') > -1:
                    href_tag = href_tag.partition('=')[2]
                # Приведение некоторых названий к читаемому виду
                word = word.replace('wa.me', 'WhatsApp').replace('vk.me', 'VK Messenger') \
                       .replace('tele.click', 'Telegram')
                messengers_links[word] = href_tag
    return messengers_links