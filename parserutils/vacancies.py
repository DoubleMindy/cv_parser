import requests
import re

from bs4 import BeautifulSoup
from lxml import html


def find_vacancy(domain, MAX_ITERS=10):
    print("Finding vacancy...")
    vacancies = []
    search_words = ['Обязанности', 'Требования', 'Опыт работы']
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    for word in search_words: 
        tag = html.fromstring(response.text).xpath("//*[contains(text(), '{0}')]".format(word))
        if tag: 
            for t_with_text in tag:
                text_to_append = ''
                iters = 0
                while text_to_append.count(word) < 2 and iters < MAX_ITERS and t_with_text:
                    t_with_text = t_with_text.getparent() 
                    if t_with_text:
                        vacancy_block = html.tostring(t_with_text, encoding='utf-8').decode('utf-8')
                        vacancy_text = BeautifulSoup(vacancy_block, "lxml").text
                        if vacancy_text:
                            vacancy_text = " ".join(vacancy_text.split())
                            if vacancy_text.count(word) < 2:
                                text_to_append = vacancy_text
                    iters += 1
                vacancies.append(text_to_append)
            return vacancies