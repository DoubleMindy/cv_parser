import requests
import pprint
import datetime
import re
from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.parse import urljoin, urlparse


EMAILS_KEYWORDS = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}'
PHONES_KEYWORDS = r'[+7-8]{1,2}[-\s(]{0,3}[0-9]{3}[)\s-]{0,3}[0-9]{3}[-\s]{0,3}[0-9]{2}[-\s]{0,3}[0-9]{2}'

# These expressions have too large complexity so I used not regular expression to find address
# ADDRESS_KEYWORDS_STREET = r'[^\>]*[А-Я].*[\n]{0,1}.*(ул){1}(ица){0,1}[\.\s]+[А-Я][^\>]*'
# ADDRESS_KEYWORDS_PROSPECT = r'[^\>]*(г){0,1}(гор){0,1}(ород){0,1}[\.\s]+[А-Я].*[\n]{0,1}.*(пр){1}(оспект){0,1}[\.\s]+[А-Я][^\>]*'

ADDRESSES = ['улица', 'ул. ', 'проезд', ' пр.', 'пр.-т', ' д.']
CONTACT_KEYWORDS = ['contact', 'контакты', 'контактн']
ABOUT_KEYWORDS = ['about', 'kompanii', 'company', 'о компании', 'о нас']
SOCIAL_KEYWORDS = ['facebook', 'instagram', 'youtube.com', 'vk.com', 'ok.ru', 'twitter', 'pinterest']
MESSENGERS_KEYWORDS = ['whatsapp', 'viber', 'tele.click', 'wa.me', 'telegram', 'icq', 'vk.me', 'skype']
REQUIRES_KEYWORDS = [
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

def ultimate_set(l):
    uniq = []
    for i, elem_i in enumerate(l):
        for j, elem_j in enumerate(l):
            if elem_i in elem_j and i != j:
                uniq.append(elem_i)
    return [item for item in l if item not in uniq]

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def find_emails(domain):
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')
    emails_list = re.findall(re.compile(EMAILS_KEYWORDS), response.text)
    if emails_list == None:
        return None
    emails_list = sorted(set(emails_list), key=emails_list.index)

    # if emails in struct <ul> <li></li> <li></li> <li></li> </ul>
    emails_info = dict()
    for email in emails_list:
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li'):
                if li.find(text = email):
                    try:
                        emails_info[email] = li.find('span').text
                    except AttributeError:
                        emails_info[email] = None


    for email in emails_list:
        if email not in emails_info.keys():
            emails_info[email] = None
    return emails_info


def find_phones(domain):
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')
    phones_list = re.findall(re.compile(PHONES_KEYWORDS), response.text)

    if phones_list == None:
        return None

    li_list = []
    phones_info = dict()
    phones_set = set(phones_list)

    # if emails in struct <ul> <li></li> <li></li> <li></li> </ul>
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
    for phone in phones_set:
        phone = re.sub('[^\+0-9]+', '', phone)
        if phone not in phones_info.keys():
            phones_info[phone] = None

    return delete_duplicate_values(phones_info)


def find_about(domain):
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts) 
    for t in visible_texts:
        if len(t.strip()) > 150:
            return t.strip()
    try:
        return max(visible_texts, key=len)
    except ValueError:
        return None

def find_social_networks(domain):
    networks_links = dict()
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = soup.find_all('a')
    for word in SOCIAL_KEYWORDS:
        for link in all_links:
            href_tag = link.get('href')
            if not href_tag:
                continue
            if href_tag.find(word) > -1:
                networks_links[word] = href_tag
    return networks_links

def find_messengers(domain):
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

def find_requires(domain):
    requires_list = []
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    for word in REQUIRES_KEYWORDS:
        regex_result = re.search(re.compile(word), response.text)
        if regex_result:
            regex_result = regex_result.group(0)
            requires_list.append(regex_result)
    return requires_list

def find_address(domain):
    addresses_list = []
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts) 
    for t in visible_texts:
        for word in ADDRESSES:
            t = ' '.join(t.split()).replace('\n', '')
            if t.find(word) > -1:
                addresses_list.append(t)
    return ultimate_set(set(addresses_list))

    # town_results = re.finditer(re.compile(ADDRESS_KEYWORDS_PROSPECT), response.text)
    # for town in town_results:
    #    print(town.group())
        # Excepting {year}{letter} and {word}{letter}
    #    if not re.search(re.compile(r'[\d]+г'), town.group()) \
    #    and not re.search(re.compile(r'[а-яА-Яa-zA-Z]+г'), town.group()):
    #        cleantext = BeautifulSoup(town.group(), "lxml").text
    #        addresses_list.append(cleantext)
    #return addresses_list

def fast_find_page(domain, soup, keywords):
    for word in keywords:
        for link in soup.find_all('a', href=True):
            if re.search(re.compile(word, re.I), link.get('href')):
                return urljoin(domain, link.get('href'))

def find_page(domain, soup, keywords):
    for word in keywords:
        for link in soup.find_all('a'):
            if re.search(re.compile(word, re.I), link.text):
                if not link.get('href'):
                    continue
                return urljoin(domain, link.get('href'))

def parse_driver(domain, callback):
    temp_list = list()
    founded_info = callback(domain)
    if founded_info not in [None, {}, ''] and founded_info not in temp_list:
        temp_list.append(founded_info)
    return temp_list

def parse(domain):
    if domain[:4] != "http":
        domain = "http://" + domain
    if domain[:-1] != '/':
        domain += '/'
    print(domain)

    item = dict()

    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')

    item['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    item['company_name'] = soup.title.string

    item['contacts_link'] = fast_find_page(domain, soup, CONTACT_KEYWORDS)
    if not item['contacts_link']:
        item['contacts_link'] = find_page(domain, soup, CONTACT_KEYWORDS)

    item['about_link'] = fast_find_page(domain, soup, ABOUT_KEYWORDS)
    if not item['contacts_link']:
        item['about_link'] = find_page(domain, soup, ABOUT_KEYWORDS)

    drive_args = [
    (item['contacts_link'], 'emails', find_emails),
    (item['about_link'], 'about', find_about),
    (item['contacts_link'], 'phones', find_phones),
    (item['contacts_link'], 'social_networks', find_social_networks),
    (item['contacts_link'], 'messengers', find_messengers),
    (item['contacts_link'], 'requires', find_requires),
    (item['contacts_link'], 'address', find_address),
    ]


    for args in drive_args:
        print("Finding {} page...".format(args[1]))
        item[args[1]] = parse_driver(args[0], args[2])
    return item

parsed_data = parse('ivanovotextil.ru')
pprint.pprint(parsed_data, indent = 4, width = 100)
