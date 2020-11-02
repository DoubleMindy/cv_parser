import requests

from bs4 import BeautifulSoup


MESSENGERS_KEYWORDS = ['whatsapp', 'viber', 'tele.click', 'wa.me', 'telegram', 'icq', 'vk.me', 'skype']


def find_messengers(domain):
    print("Finding messengers...")
    messengers_links = dict()
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = soup.find_all('a')
    for word in MESSENGERS_KEYWORDS:
        for link in all_links:
            href_tag = link.get('href')
            if not href_tag:
                continue
            if href_tag.find(word) > -1:
                if href_tag.find('=') > -1:
                    href_tag = href_tag.partition('=')[2]
                word = word.replace('wa.me', 'WhatsApp').replace('vk.me', 'VK Messenger') \
                       .replace('tele.click', 'Telegram')
                messengers_links[word] = href_tag
    return messengers_links