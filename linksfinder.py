import requests
import os.path
import re

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def find_page_by_urls(domain, keywords, soup=None):
    if soup is None:
        response = requests.get(domain)
        soup = BeautifulSoup(response.text, 'html.parser')
    for word in keywords:
        for link in soup.find_all('a', href=True):
            if re.search(re.compile(word, re.I), link.get('href')):
                return urljoin(domain, link.get('href'))


def find_page_by_keywords(domain, keywords, soup=None):
    if soup is None:
        response = requests.get(domain)
        soup = BeautifulSoup(response.text, 'html.parser')
    for word in keywords:
        for link in soup.find_all('a', href=True):
            if re.search(re.compile(word, re.I), link.text):
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