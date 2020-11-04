from _utilities_ import tag_visible, get_request

from bs4 import BeautifulSoup


def get_description(element):
    """
    element: soup-объект, содержащий весь текст страницы (<soup>)

    Метод просматривает мета-теги страницы, находя в них описание

    return: мета-описание страницы (str)
    """
    description = None
    if element.find("meta", property="description"):
        description = element.find("meta", property="description").get('content')
    elif element.find("meta", property="og:description"):
        description = element.find("meta", property="og:description").get('content')
    elif element.find("meta", property="facebook:description"):
        description = element.find("meta", property="facebook:description").get('content')
    elif element.find("p"):
        description = element.find("p")
    return description


def find_about(domain, ABOUT_MIN_DESC=150):
    """
    domain: доменное имя страницы "О компании" (str)

    ABOUT_MIN_DESC: минимальная длина предполагаемого текста-описания (Optional str)

    return: описание компании (str)
    """

    print("Finding about page...")

    response = get_request(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    description =  get_description(soup)
    if description:
        return str(description)
    texts = soup.findAll(text=True)
    # Из всех текстов оставляем только те, что видны на странице
    visible_texts = filter(tag_visible, texts) 

    for text in visible_texts:
        if len(text.strip()) > ABOUT_MIN_DESC:
            return text.strip()
    return