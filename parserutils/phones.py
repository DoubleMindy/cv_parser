import requests
import re

from bs4 import BeautifulSoup
from lxml import html


PHONES_KEYWORDS = r'[+7-8]{1,2}[-\s(]{0,3}[0-9]{3}[)\s-]{0,3}[0-9]{3}[-\s]{0,3}[0-9]{2}[-\s]{0,3}[0-9]{2}'


def delete_duplicate_values(d):
    temp = [] 
    res = {}
    for key, val in d.items(): 
        if val not in temp or val is None: 
            temp.append(val) 
            res[key] = val 
    return res


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
        if phone not in phones_info.keys():
            phone = re.sub('[^\+0-9]+', '', phone)
            phones_info[phone] = None
    return delete_duplicate_values(phones_info)
