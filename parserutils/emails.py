import requests
import re

from bs4 import BeautifulSoup
from lxml import html


EMAILS_KEYWORDS = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}'


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