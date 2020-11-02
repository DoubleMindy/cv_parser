import requests

from bs4 import BeautifulSoup


SOCIAL_KEYWORDS = ['facebook', 'instagram', 'youtube.com', 'vk.com', 'ok.ru', 'twitter', 'pinterest']


def find_social_networks(domain):
    print("Finding social networks...")
    networks_links = dict()
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = soup.find_all('a', href=True)
    for word in SOCIAL_KEYWORDS:
        for link in all_links:
            href_tag = link.get('href')
            if href_tag.find(word) > -1:
                networks_links[word] = href_tag
    return networks_links