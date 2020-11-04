from _utilities_ import get_request, \
find_description_around, find_content_around
import re

from bs4 import BeautifulSoup
from lxml import html


NAMES_KEYWORDS = r'[А-Я]{1}[а-я]+\s[А-Я]{1}[а-я]+'
FULLNAMES_KEYWORDS = r'([А-Я]{1}[а-я]+\s){2}[А-Я]{1}[а-я]+'

# Слова, которые могут ошибочно приниматься за имя
STOP_WORDS = ['Россия', 'Москва', 'Copyright', 'Написать', 
              'Позвонить', 'Директор', 'Российской Федерации', 
              'Российская Федерация', 'Частые Вопросы', 
              'Проспект', 'Площадь', 'Храм']


def find_team(domain, MAX_ITERS=10, MIN_LEN=9):
    """
    domain: доменное имя страницы "Наша команда" (str)
    MAX_ITERS: максимальное число родительских блоков для поиска (Optional int)
    MIN_DESC: минимальная длина строки с описанием должности (Optional int)

    return: информация о сотрудниках компании, содержащая имя, должность,
    ссылку на страницу сотрудника и ссылку на фото (dict)
    """
    print("Finding team...")
    all_employees = []
    response = get_request(domain)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Ищется либо три слова, начинающихся с заглавной буквы, либо два слова 
    # (если на странице сотрудники без отчества)
    employees_iterator = re.finditer(re.compile(FULLNAMES_KEYWORDS), response.text)
    if not any(employees_iterator):
        employees_iterator = re.finditer(re.compile(NAMES_KEYWORDS), response.text)

    employees_prelist = [empl.group(0) for empl in employees_iterator]
    employees_prelist = sorted(set(employees_prelist), key=employees_prelist.index)

    # Исключение стоп-слов
    for employee in employees_prelist:
        for word in STOP_WORDS:
            if employee.find(word) > -1:
                employees_prelist.remove(employee)
    for employee in employees_prelist:
        employee_blocks = html.fromstring(response.text).xpath("//*[contains(text(), '{0}')]".format(employee))
        # Будем искать текст, пока его длина не будет больше пороговой
        # (или пока не достигнем максимального значения итераций)
        iters = 0
        person_text = ''
        for tag in employee_blocks:
            while iters < MAX_ITERS and not len(person_text) > MIN_LEN:
                tag = tag.getparent()
                person_block = html.tostring(tag, encoding='utf-8').decode('utf-8')
                person_text = BeautifulSoup(person_block, "lxml").text
                iters += 1
                if person_text:
                    # Исключаем из должности имя сотрудника
                    person_text = person_text.replace('\n', ' ').replace(employee, '').replace('\t', '')
                    person_text = " ".join(person_text.split())

        if person_text not in all_employees:
            href = find_content_around(response, employee, 'href=\".*\"', MAX_ITERS=1) 
            if href:
                href = href.replace('href=', '').replace('\"', '')

            photo = find_content_around(response, employee, 'src=\".*\.(jpg|png)\"', MAX_ITERS=3)
            if photo:
                photo = photo.replace('src=', '').replace('\"', '')

            all_employees.append(
                                {'name': employee, 
                                'info': person_text,
                                'link': href,
                                'photo': photo
                                })
    return all_employees
