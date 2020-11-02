import requests
import re

from bs4 import BeautifulSoup
from lxml import html

NAMES_KEYWORDS = r'[А-Я]{1}[а-я]+\s[А-Я]{1}[а-я]+'
FULLNAMES_KEYWORDS = r'([А-Я]{1}[а-я]+\s){2}[А-Я]{1}[а-я]+'


def find_team(domain, MAX_ITERS=10, MIN_DESC=10):
    print("Finding team...")
    employees_prelist = []
    all_employees = []
    stop_words = ['Россия', 'Москва', 'Copyright', 'Написать', 'Позвонить', 'Директор',
    'Российской Федерации', 'Российская Федерация', 'Частые Вопросы', 'Проспект', 'Площадь', 'Храм']
    response = requests.get(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    employees_iterator = re.finditer(re.compile(FULLNAMES_KEYWORDS), response.text)
    if not employees_iterator:
        employees_iterator = re.finditer(re.compile(NAMES_KEYWORDS), response.text)

    for empl_pointer in employees_iterator:
        employees_prelist.append(empl_pointer.group(0))

    employees_prelist = sorted(set(employees_prelist), key=employees_prelist.index)
    for employee in employees_prelist:
        for word in stop_words:
            if employee.find(word) > -1:
                employees_prelist.remove(employee)

    for employee in employees_prelist:
        tag = html.fromstring(response.text).xpath("//*[contains(text(), '{0}')]".format(employee))
        employee_data = []
        photo = person_text = href = ''
        for t_with_text in tag:
            t = t_with_text
            person_block = html.tostring(t.getparent(), encoding='utf-8').decode('utf-8')
            search_for_href = re.search(re.compile('href=\".*\"'), person_block)
            if search_for_href:
                href = search_for_href.group(0).replace('href=', '').replace('\"', '')

            iters = 0
            while not photo and iters < MAX_ITERS:
                t = t.getparent()
                person_block = html.tostring(t, encoding='utf-8').decode('utf-8')
                search_for_photo = re.search(re.compile('src=\".*\.(jpg|png)\"'), person_block)
                iters += 1
                if search_for_photo:
                    photo = search_for_photo.group(0).replace('src=', '').replace('\"', '')

            iters = 0
            while iters < MAX_ITERS and not len(person_text) > MIN_DESC:
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