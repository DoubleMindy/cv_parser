import requests

from bs4 import BeautifulSoup
from bs4.element import Comment


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def get_description(html):
    description = None
    if html.find("meta", property="description"):
        description = html.find("meta", property="description").get('content')
    elif html.find("meta", property="og:description"):
        description = html.find("meta", property="og:description").get('content')
    elif html.find("meta", property="facebook:description"):
        description = html.find("meta", property="facebook:description").get('content')
    elif html.find("p"):
        description = html.find("p").contents
    return description


def find_about(domain):
    print("Finding about page...")
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts) 
    for t in visible_texts:
        if len(t.strip()) > 150:
            return t.strip()
    return get_description(soup)