from bs4 import BeautifulSoup


def get_title(soup):
    """
    domain: soup-объект главной страницы (<soup>)

    return: None или мета-заголовок страницы (str)
    """
    title = None
    if soup.title.string:
        title = soup.title.string
    elif soup.find("meta", property="og:title"):
        title = soup.find("meta", property="og:title").get('content')
    elif soup.find("meta", property="facebook:title"):
        title = soup.find("meta", property="facebook:title").get('content')
    elif soup.find("h1"):
        title = soup.find("h1").string
    return title