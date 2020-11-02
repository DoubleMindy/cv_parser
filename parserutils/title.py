from bs4 import BeautifulSoup


def get_title(html):
    title = None
    if html.title.string:
        title = html.title.string
    elif html.find("meta", property="og:title"):
        title = html.find("meta", property="og:title").get('content')
    elif html.find("meta", property="facebook:title"):
        title = html.find("meta", property="facebook:title").get('content')
    elif html.find("h1"):
        title = html.find("h1").string
    return title