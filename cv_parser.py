import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse


EMAILS = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}'
PHONES = r'[+7-8]{1,2}[-\s(]{0,3}[0-9]{3}[)\s-]{0,3}[0-9]{3}[-\s]{0,3}[0-9]{2}[-\s]{0,3}[0-9]{2}'

CONTACT_KEYWORDS = ['контакты', 'contact', 'контактн']
ABOUT_KEYWORDS = ['о нас', 'о компании']
SOCIAL_KEYWORDS = ['facebook', 'whatsapp', 'telegram', 'instagram', 'vk.com', 'viber']


def find_emails(domain):
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')
    emails_list = re.findall(re.compile(EMAILS), response.text)
    if emails_list == None:
        return None
    emails_list = sorted(set(emails_list), key=emails_list.index)

    # if emails in struct <ul> <li></li> <li></li> <li></li> </ul>
    emails_info = dict()
    for email in emails_list:
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li'):
                if li.find(text = email):
                    emails_info[email] = li.find('span').text

    for email in emails_list:
        if email not in emails_info.keys():
            emails_info[email] = None
    return emails_info


def find_phones(domain):
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')
    phones_list = re.findall(re.compile(PHONES), response.text)
    if phones_list == None:
        return None
    phones_list_cleared = [phones.replace(' ', '').replace(')', '').replace('(', '') \
                                  .replace('+7', '8').replace('-', '') \
                   for phones in phones_list]
    phones_list_cleared = sorted(set(phones_list_cleared), key=phones_list_cleared.index)

    # if emails in struct <ul> <li></li> <li></li> <li></li> </ul>
    phones_info = dict()
    for phone in phones_list:
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li'):
                if li.find(text = phone):
                    try:
                        phones_info[li.find('span').text] = phone 
                    except AttributeError:
                        phones_info[phone] = phone

    phone_checklist = [phones.replace(' ', '').replace(')', '').replace('(', '') \
                                  .replace('+7', '8').replace('-', '') \
                   for phones in phones_info.values()]

    for phone in phones_list_cleared:
        if phone not in phone_checklist:
            phones_info[phone] = None

    return phones_info


def find_about(domain):
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')
    about_info = soup.find('p')
    if about_info == None:
        return None
    return about_info.text 

def find_messengers(domain):
    messengers_links = dict()
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')

    all_links = soup.findAll('a')
    for link in all_links:
        for word in SOCIAL_KEYWORDS:
            href_tag = link.get('href')
            if not href_tag:
                return None
            if href_tag.find(word) > -1:
                messengers_links[word] = link.get('href')

    return messengers_links


def parse(domain):
    if domain[:4] != "http":
        domain = "http://" + domain
    if domain[:-1] != '/':
        domain += '/'
    print(domain)

    item = dict()

    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'lxml')

    # Company name grabber:
    item['company_name'] = soup.title.string

    # Email grabber:
    temp_list = list()
    for word in CONTACT_KEYWORDS:
        for link in soup.find_all('a'):
            if re.findall(re.compile(word, re.I), link.text):
                if not link.get('href'):
                    continue
                print("Link of emails", link.get('href'))
                link_to_follow = urljoin(domain, link.get('href'))
                founded_info = find_emails(link_to_follow)
                if founded_info not in [None, {}, ''] and founded_info not in temp_list:
                    temp_list.append(founded_info)
    item['emails'] = temp_list

    # Info grabber:
    temp_list = list()
    for word in ABOUT_KEYWORDS:
        for link in soup.find_all('a'):
            if re.findall(re.compile(word, re.I), link.text):
                if not link.get('href'):
                    continue
                print("Link of about", link.get('href'))
                link_to_follow = urljoin(domain, link.get('href'))
                founded_info = find_about(link_to_follow)
                if founded_info not in [None, {}, ''] and founded_info not in temp_list:
                    temp_list.append(founded_info)
    item['about'] = temp_list

    # Phones grabber:
    temp_list = list()
    for word in CONTACT_KEYWORDS:
        for link in soup.find_all('a'):
            if re.findall(re.compile(word, re.I), link.text):
                if not link.get('href'):
                    continue
                link_to_follow = urljoin(domain, link.get('href'))
                founded_info = find_phones(link_to_follow)
                if founded_info not in [None, {}, ''] and founded_info not in temp_list:
                    temp_list.append(founded_info)
    item['phones'] = temp_list

    # Messenger grabber:
    temp_list = list()
    for word in CONTACT_KEYWORDS:
        for link in soup.find_all('a'):
            if re.findall(re.compile(word, re.I), link.text):
                if not link.get('href'):
                    continue
                link_to_follow = urljoin(domain, link.get('href'))
                founded_info = find_messengers(link_to_follow)
                if founded_info not in [None, {}, ''] and founded_info not in temp_list:
                    temp_list.append(founded_info)
    item['messengers'] = temp_list

    return item


parsed_data = parse('autostrong-m.ru')
print(parsed_data)