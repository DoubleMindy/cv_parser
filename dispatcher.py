import datetime

from bs4 import BeautifulSoup

from _utilities_ import get_request
from parserutils import emails, phones, social_networks, \
                        messengers, requisites, addresses, \
                        title, team, about, vacancies
from linksfinder import find_page_by_keywords, find_all_pages, \
                        find_page_by_urls


CONTACT_KEYWORDS = ['контакты', 'контактн']
CONTACT_URLS = ['contact', 'kontakty', 'kontakti']

TEAM_KEYWORDS = ['команда', 'сотрудники', 'коллектив']
TEAM_URLS = ['staff', 'personal']

ABOUT_KEYWORDS = ['об учреждении', 'о компании', 'о нас']
ABOUT_URLS = ['about', 'kompanii', 'company']

VACANCY_KEYWORDS = ['вакансии', 'стажировк']
VACANCY_URLS = ['vacanc', 'vakans']


def parse_driver(domain, callback):
    """
    domain: страница, к которой будет применена функция парсера (str)
    callback: функция по нахождению элемента страницы (def)

    Диспетчер, вызывающий определенную функцию

    return: информация, которую нашла функция парсера (dict, list, str)
    """
    founded_info = callback(domain)
    if founded_info not in [None, {}, '']:
        return founded_info
    return


def parse(domain, deep_test=False):
    """
    domain: основная страница для всего парсера (str)
    deep_test: режим разработчика (Optional bool)

    Основная функция, вызываемая в мэйне, которая, в свою очередь,
    поочередно вызывает все возможные методы парсера и складывает 
    результат в словарь

    return: вся информация, полученная парсером (dict)
    """
    if domain[:4] != "http":
        domain = "http://" + domain
    if domain[-1] == '/':
        domain = domain[:-1]
    # Приведение url к виду http://domain.com

    print("Start parsing {}...".format(domain))

    result = dict()

    DRIVE_ARGS = [
                  ('emails', emails.find_emails),
                  ('phones', phones.find_phones), 
                  ('social_networks', social_networks.find_social_networks),
                  ('messengers', messengers.find_messengers), 
                  ('requisites', requisites.find_requisites),
                  ('address', addresses.find_address),
                 ]

    response = get_request(domain)
    if not response:
        exit()
    soup = BeautifulSoup(response.text, 'lxml')

    result['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    result['main_link'] = domain
    result['company_name'] = title.get_title(soup)
    
    result['company_links'] = list()

    contacts_link = find_page_by_urls(domain, CONTACT_URLS, soup)
    # Костыль: если нашли первый попавшийся url, не содержащий адреса и почты,
    # но содержащий слово kontakt, это может быть не страница контактов, а нечто похожее
    # (пример: domain.com/kontakntie-usiliteli). Тогда ищем по ключевым словам в меню
    if not contacts_link or (not addresses.find_address(contacts_link) 
                             and emails.find_emails(contacts_link)):
        contacts_link = find_page_by_keywords(domain, CONTACT_KEYWORDS, soup)

    # Тестовый режим
    if deep_test:
        contacts_links = find_all_pages(find_all_pages)
        print(contacts_links)

    about_link = find_page_by_keywords(domain, ABOUT_KEYWORDS, soup)
    if not about_link:
        about_link = find_page_by_urls(domain, ABOUT_URLS, soup)

    if not about_link:
        result['about'] = None
    else:
        result['about'] = parse_driver(about_link, about.find_about)

    vacancy_link = find_page_by_keywords(contacts_link, VACANCY_KEYWORDS, soup)
    if not vacancy_link:
        vacancy_link = find_page_by_urls(contacts_link, VACANCY_URLS, soup)

    if not vacancy_link:
        result['vacancies'] = None
    else:
        result['vacancies'] = parse_driver(vacancy_link, vacancies.find_vacancy)

    # Переходы к странице "Наша команда" ищем везде где можно и по чему можно
    team_link = find_page_by_keywords(domain, TEAM_KEYWORDS, soup)
    if not team_link:
        team_link = find_page_by_keywords(contacts_link, TEAM_KEYWORDS, soup)
    if not team_link:
        team_link = find_page_by_keywords(about_link, TEAM_KEYWORDS, soup)
    if not team_link:
        team_link = find_page_by_urls(domain, TEAM_URLS, soup)

    if not team_link:
        result['team'] = None
    else:
        result['team'] = parse_driver(team_link, team.find_team)
    
    # Если нашли страницу с контактами, то парсим контакты же по ней
    if contacts_link:
        for args in DRIVE_ARGS:
            result[args[0]] = parse_driver(contacts_link, args[1])
    else:
    # ...Или пытаемся вытащить что-то прямо с главной
        for args in DRIVE_ARGS:
            result[args[0]] = parse_driver(domain, args[1])

    result['company_links'] = {
                             'contacts': contacts_link,
                             'about': about_link,
                             'vacancies': vacancy_link,
                             'staff': team_link
                            }
    return result