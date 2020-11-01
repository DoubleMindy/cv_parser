import requests
import pprint
import datetime
import os.path
import re
import itertools
import html as decoder

from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.parse import urljoin, urlparse
from lxml import html

EMAILS_KEYWORDS = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}'
PHONES_KEYWORDS = r'[+7-8]{1,2}[-\s(]{0,3}[0-9]{3}[)\s-]{0,3}[0-9]{3}[-\s]{0,3}[0-9]{2}[-\s]{0,3}[0-9]{2}'
NAMES_KEYWORDS = r'[А-Я]{1}[а-я]+\s[А-Я]{1}[а-я]+'

# These expressions have too large complexity so I used not regular expression to find address
# ADDRESS_KEYWORDS_STREET = r'[^\>]*[А-Я].*[\n]{0,1}.*(ул){1}(ица){0,1}[\.\s]+[А-Я][^\>]*'
# ADDRESS_KEYWORDS_PROSPECT = r'[^\>]*(г){0,1}(гор){0,1}(ород){0,1}[\.\s]+[А-Я].*[\n]{0,1}.*(пр){1}(оспект){0,1}[\.\s]+[А-Я][^\>]*'

ADDRESSES = ['г. ', 'улица', 'ул. ', 'проезд', ' пр.', 'пр.-т', ' д.']
CONTACT_KEYWORDS = ['contact', 'kontakty', 'kontakti', 'контакты', 'контактн']
TEAM_KEYWORDS = ['команда', 'сотрудники', 'коллектив', 'персонал']
TEAM_URLS = ['staff', 'personal']
ABOUT_KEYWORDS = ['about', 'kompanii', 'company', 'об учреждении', 'о компании', 'о нас']
SOCIAL_KEYWORDS = ['facebook', 'instagram', 'youtube.com', 'vk.com', 'ok.ru', 'twitter', 'pinterest']
MESSENGERS_KEYWORDS = ['whatsapp', 'viber', 'tele.click', 'wa.me', 'telegram', 'icq', 'vk.me', 'skype']
REQUISITES_KEYWORDS = [
r'ИНН[\s\:0-9]+', 
r'БИК[\s\:0-9]+', 
r'КПП[\s\:0-9]+', 
r'[Рр]{1}асч[её]{1}тный сч[её]{1}т[\s\:0-9]+',
]


def delete_duplicate_values(d):
    temp = [] 
    res = {}
    for key, val in d.items(): 
        if val not in temp or val is None: 
            temp.append(val) 
            res[key] = val 
    return res


def delist(l):
    return [item for sublist in l for item in sublist]


def ultimate_set(l):
    uniq = []
    for i, elem_i in enumerate(l):
        for j, elem_j in enumerate(l):
            if elem_i in elem_j and i != j and len(elem_i) >= len(elem_j):
                uniq.append(elem_i)
    return [item for item in l if item not in uniq]


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def get_title(html):
    title = None
    if html.title.string:
        title = html.title.string
    elif html.find("meta", property="og:title"):
        title = html.find("meta", property="og:title").get('content')
    elif html.find("meta", property="twitter:title"):
        title = html.find("meta", property="twitter:title").get('content')
    elif html.find("h1"):
        title = html.find("h1").string
    return title


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


def find_emails(domain):
    print("Finding emails...")
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')
    emails_list = re.findall(re.compile(EMAILS_KEYWORDS), response.text)

    if emails_list == None:
        return None

    emails_list = sorted(set(emails_list), key=emails_list.index)

    emails_info = dict()
    for email in emails_list:
        tag = html.fromstring(response.content).xpath("//*[contains(text(), '{0}')]".format(email))
        for t in tag:
            email_block = html.tostring(t.getparent(), encoding='utf-8').decode('utf-8')  
            clean_text = BeautifulSoup(email_block, "lxml").text
            if re.search('[а-яА-Я]+', clean_text):
                clean_info = re.search('[а-яА-Я]+.*', clean_text).group(0)
                if not email in emails_info.values():
                    emails_info[email] = clean_info

    for email in emails_list:
        if email not in emails_info.keys():
            emails_info[email] = None
    return emails_info


def find_phones(domain):
    print("Finding phones...")
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')
    phones_list = re.findall(re.compile(PHONES_KEYWORDS), response.text)

    if phones_list == None:
        return None

    li_list = []
    phones_info = dict()
    phones_set = set(phones_list)
    for phone in phones_set:
        tag = html.fromstring(response.content).xpath("//*[contains(text(), '{0}')]".format(phone))
        for t in tag:
            phone_block = html.tostring(t.getparent(), encoding='utf-8').decode('utf-8')  
            clean_text = BeautifulSoup(phone_block, "lxml").text
            if re.search('[а-яА-Я]+', clean_text):
                clean_info = re.search('[а-яА-Я]+.*', clean_text).group(0)
                if not phone in phones_info.values():
                    phones_info[phone] = clean_info.replace(phone, '')

    for phone in phones_set:
        phone = re.sub('[^\+0-9]+', '', phone)
        if phone not in phones_info.keys():
            phones_info[phone] = None
    return delete_duplicate_values(phones_info)


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


def find_requisites(domain):
    print("Finding requisites...")
    requisites_list = []
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    for word in REQUISITES_KEYWORDS:
        regex_result = re.search(re.compile(word), response.text)
        if regex_result:
            regex_result = regex_result.group(0)
            requisites_list.append(regex_result)
    return requisites_list


def find_address(domain):
    print("Finding addresses...")
    addresses_list = []
    stop_words = ['такси', 'автобус', 'маршрутка', 'трамвай']
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts) 

    for t in visible_texts:
        for word in ADDRESSES:
            t = ' '.join(t.split()).replace('\n', '')
            if t.find(word) > -1 and not re.search(re.compile(r'[\d]+г'), t) \
            and not re.search(re.compile(r'[а-яА-Яa-zA-Z]+г'), t) and re.search(re.compile(r'[\d]+'), t):
                addresses_list.append(t)

    addresses_info = ultimate_set(set(addresses_list))
    bad_addresses = []
    for word in stop_words:
        for addr in addresses_info:
            if addr.find(word) > -1:
                bad_addresses.append(addr)
    return [item for item in addresses_info if item not in bad_addresses]


def find_team(domain):
    print("Finding team...")
    employees_prelist = []
    all_employees = []
    stop_words = ['Россия', 'Москва', 'Copyright', 'Написать', 'Позвонить', 
    'Российской Федерации', 'Российская Федерация', 'Частые Вопросы', 'Проспект', 'Площадь', 'Храм']
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    employees_prelist = re.findall(re.compile(NAMES_KEYWORDS), response.text)
    employees_prelist = sorted(set(employees_prelist), key=employees_prelist.index)
    for employee in employees_prelist:
        for word in stop_words:
            if employee.find(word) > -1:
                employees_prelist.remove(employee)

    for employee in employees_prelist:
        tag = html.fromstring(response.text).xpath("//*[contains(text(), '{0}')]".format(employee))
        #if tag.find('Element a at') > -1
        employee_data = []
        photo = person_text = href = None
        for t_with_text in tag:
            t = t_with_text
            person_block = html.tostring(t.getparent(), encoding='utf-8').decode('utf-8')
            search_for_href = re.search(re.compile('href=\".*\"'), person_block)
            if search_for_href:
                href = search_for_href.group(0).replace('href=', '').replace('\"', '')

            iters = 0
            while not photo or iters < 10:
                t = t.getparent()
                person_block = html.tostring(t, encoding='utf-8').decode('utf-8')
                search_for_photo = re.search(re.compile('src=\".*\.(jpg|png)\"'), person_block)
                iters += 1
                if search_for_photo:
                    photo = search_for_photo.group(0).replace('src=', '').replace('\"', '')

            iters = 0
            while not person_text or iters < 4:
                t_with_text = t_with_text.getparent()
                person_block = html.tostring(t_with_text, encoding='utf-8').decode('utf-8')
                person_text = BeautifulSoup(person_block, "lxml").text
                iters += 1
                if person_text:
                    person_text = person_text.replace('\n', ' ').replace(employee, '').replace('\t', '')
                    person_text = " ".join(person_text.split())

            if person_text not in all_employees:
                all_employees.append(
                    {'name': employee, 
                     'info': person_text,
                     'link': href,
                     'photo': photo
                    })
    return all_employees


def find_page_by_urls(domain, keywords, soup=None):
    if soup is None:
        response = requests.get(domain)
        soup = BeautifulSoup(response.text, 'html.parser')
    for word in keywords:
        for link in soup.find_all('a', href=True):
            if re.search(re.compile(word, re.I), link.get('href')):
                return urljoin(domain, link.get('href'))


def find_subpages(domain, path_to_search, soup=None):
    all_links = []
    if soup is None:
        response = requests.get(domain)
        soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a', href=True):
        if re.findall(re.compile(path_to_search, re.I), link.get('href')) \
        and link.get('href') != path_to_search and link.get('href').find('/en/') == -1:
            all_links.append(urljoin(domain, link.get('href')))
    if len(all_links):
        return list(set(all_links))
    return 


def find_deep_contacts(contacts_link):
    path = urlparse(contacts_link).path
    while os.path.dirname(path) != '/':
        path = os.path.dirname(path)

    sublinks = find_subpages(contacts_link, path)
    if sublinks:
        main_contacts_sublinks = []
        main_contacts_sublinks.append(''.join(contacts_link))
        if len(sublinks) == 1:
            main_contacts_sublinks.append(''.join(sublinks))
        else:
            main_contacts_sublinks = [i for i in sublinks if i]

        all_contacts_sublinks = main_contacts_sublinks.copy()

        for contact_domain in main_contacts_sublinks:
            path = urlparse(contact_domain).path
            subpages = find_subpages(contact_domain, path)
            if subpages:
                all_contacts_sublinks += subpages
    return all_contacts_sublinks


def find_page_by_keywords(domain, keywords, soup=None):
    if soup is None:
        response = requests.get(domain)
        soup = BeautifulSoup(response.text, 'html.parser')
    for word in keywords:
        for link in soup.find_all('a', href=True):
            if re.search(re.compile(word, re.I), link.text):
                return urljoin(domain, link.get('href'))


def parse_driver(domain, callback):
    temp_list = list()
    founded_info = callback(domain)
    if founded_info not in [None, {}, ''] and founded_info not in temp_list:
        temp_list.append(founded_info)
    return temp_list


def parse(domain, deep_test=False):
    if domain[:4] != "http":
        domain = "http://" + domain

    print(domain)

    item = dict()
    DRIVE_ARGS = [
    ('emails', find_emails),
    ('phones', find_phones), 
    ('social_networks', find_social_networks),
    ('messengers', find_messengers), 
    ('requisites', find_requisites),
    ('address', find_address),
    ]

    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')

    item['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    item['main_link'] = domain
    item['company_name'] = get_title(soup)

    item['contacts_link'] = find_page_by_urls(domain, CONTACT_KEYWORDS, soup)
    if not item['contacts_link'] or not find_address(item['contacts_link']):
        item['contacts_link'] = find_page_by_keywords(domain, CONTACT_KEYWORDS, soup)

    if deep_test:
        item['contacts_link'] = find_deep_contacts(item['contacts_link'])

    item['about_link'] = find_page_by_keywords(domain, ABOUT_KEYWORDS, soup)
    if not item['about_link']:
        item['about_link'] = find_page_by_urls(domain, ABOUT_KEYWORDS, soup)
    if not item['about_link']:
        item['about'] = None
    else:
        item['about'] = parse_driver(item['about_link'], find_about)

    item['team_link'] = find_page_by_keywords(domain, TEAM_KEYWORDS, soup)
    if not item['team_link']:
        item['team_link'] = find_page_by_keywords(item['contacts_link'], TEAM_KEYWORDS, soup)
    if not item['team_link']:
        item['team_link'] = find_page_by_keywords(item['about_link'], TEAM_KEYWORDS, soup)
    if not item['team_link']:
        item['team_link'] = find_page_by_urls(domain, TEAM_URLS, soup)
    if not item['team_link']:
        item['team'] = None
    else:
        item['team'] = parse_driver(item['team_link'], find_team)
    
    if item['contacts_link']:
        if type(item['contacts_link']) == str:
            for args in DRIVE_ARGS:
                item[args[0]] = parse_driver(item['contacts_link'], args[1])
        else:
            for args in drive_args:
                response_list = []
                for page in item['contacts_link']:
                    response = parse_driver(page, args[1])
                    if response and response not in response_list:
                        response_list.append(response)
                item[args[0]] = [i for i in delist(response_list) if i]
    else:
        for args in DRIVE_ARGS:
            item[args[0]] = parse_driver(domain, args[1])
    return item

parsed_data = parse('giprogorproekt.ru')
pprint.pprint(parsed_data, indent = 4, width = 100)

'''
    # if phones in struct <ul> <li></li> <li></li> <li></li> </ul>
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            li_list.append(str(li)) 
    for phone in phones_set:
        for li in li_list:
            if li.find(phone) > -1:
                clean_li = BeautifulSoup(li, "lxml").text
                only_text = re.sub('[^а-яА-Я\s]+', '', clean_li)
                if only_text.isspace():
                    continue
                only_text = ' '.join(only_text.split()).replace('\n', '')
                phones_info[phone] = only_text


    for email in emails_list:
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li'):
                if li.find(text = email):
                    try:
                        emails_info[email] = li.find('span').text
                    except AttributeError:
                        emails_info[email] = None
'''
