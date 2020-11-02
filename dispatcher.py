import requests
import datetime

from bs4 import BeautifulSoup

from parserutils import emails, phones, social_networks, messengers, requisites, addresses, title, about, vacancies
from linksfinder import find_page_by_keywords, find_page_by_urls, find_deep_contacts


CONTACT_KEYWORDS = ['контакты', 'контактн']
CONTACT_URLS = ['contact', 'kontakty', 'kontakti']

TEAM_KEYWORDS = ['команда', 'сотрудники', 'коллектив', 'персонал']
TEAM_URLS = ['staff', 'personal']

ABOUT_KEYWORDS = ['об учреждении', 'о компании', 'о нас']
ABOUT_URLS = ['about', 'kompanii', 'company']

VACANCY_KEYWORDS = ['вакансии', 'стажировк']
VACANCY_URLS = ['vacanc', 'vakans']


def parse_driver(domain, callback):
    temp_list = list()
    founded_info = callback(domain)
    if founded_info not in [None, {}, ''] and founded_info not in temp_list:
        temp_list.append(founded_info)
    return temp_list


def parse(domain, deep_test=False):
    if domain[:4] != "http":
        domain = "http://" + domain
    if domain[-1] == '/':
        domain = domain[:-1]

    print("Start parsing {}...".format(domain))

    item = dict()

    DRIVE_ARGS = [
                  ('emails', emails.find_emails),
                  ('phones', phones.find_phones), 
                  ('social_networks', social_networks.find_social_networks),
                  ('messengers', messengers.find_messengers), 
                  ('requisites', requisites.find_requisites),
                  ('address', addresses.find_address),
                 ]

    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')

    item['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    item['main_link'] = domain
    item['company_name'] = title.get_title(soup)
    
    item['company_links'] = list()

    contacts_link = find_page_by_urls(domain, CONTACT_URLS, soup)
    if not contacts_link or not addresses.find_address(contacts_link):
        contacts_link = find_page_by_keywords(domain, CONTACT_KEYWORDS, soup)

    if deep_test:
        contacts_link = find_deep_contacts(contacts_link)

    about_link = find_page_by_keywords(domain, ABOUT_KEYWORDS, soup)
    if not about_link:
        about_link = find_page_by_urls(domain, ABOUT_URLS, soup)

    if not about_link:
        item['about'] = None
    else:
        item['about'] = parse_driver(about_link, about.find_about)

    vacancy_link = find_page_by_keywords(contacts_link, VACANCY_KEYWORDS, soup)
    if not vacancy_link:
        vacancy_link = find_page_by_urls(contacts_link, VACANCY_URLS, soup)

    if not vacancy_link:
        item['vacancy'] = None
    else:
        item['vacancy'] = parse_driver(vacancy_link, vacancies.find_vacancy)

    team_link = find_page_by_keywords(domain, TEAM_KEYWORDS, soup)
    if not team_link:
        team_link = find_page_by_keywords(contacts_link, TEAM_KEYWORDS, soup)
    if not team_link:
        team_link = find_page_by_keywords(about_link, TEAM_KEYWORDS, soup)
    if not team_link:
        team_link = find_page_by_urls(domain, TEAM_URLS, soup)

    if not team_link:
        item['team'] = None
    else:
        item['team'] = parse_driver(team_link, find_team)
    
    if contacts_link:
        for args in DRIVE_ARGS:
            item[args[0]] = parse_driver(contacts_link, args[1])
        '''
        if type(contacts_link) == str:
            for args in DRIVE_ARGS:
                item[args[0]] = parse_driver(contacts_link, args[1])
        else:
            for args in drive_args:
                response_list = []
                for page in contacts_link:
                    response = parse_driver(page, args[1])
                    if response and response not in response_list:
                        response_list.append(response)
                response_list = [item for response_list in l for item in response_list]
                item[args[0]] = [i for i in response_list if i]
        '''
    else:
        for args in DRIVE_ARGS:
            item[args[0]] = parse_driver(domain, args[1])

    item['company_links'] = {
                             'contacts': contacts_link,
                             'about': about_link,
                             'vacancies': vacancy_link,
                             'staff': team_link
                            }
    return item

#parsed_data = parse('cornerstone.ru')
#pprint.pprint(parsed_data, indent = 4, width = 200)