from _utilities_ import get_request, \
find_description_around, find_content_around
import re
from lxml import html

from bs4 import BeautifulSoup

SEARCH_WORDS = ['Обязанности', 'Требования', 'Опыт работы']
WORK_EXPERIENCE = r'(О|о)пыт\sработы[\:\s]+(от|От|до|До|не|Не|\d).*(года|лет|год|требуется|опыта)'
DATE_REGEX = r'([0-2][0-9]|(3)[0-1])\.(((0)[0-9])|((1)[0-2]))\.\d{4}'


def find_vacancy(domain, MAX_ITERS=10):
    """
    domain: доменное имя страницы "Вакансии" (str)
    MAX_ITERS: максимальное число родительских блоков для поиска (Optional int)

    return: информация о текущих вакансиях, каждый элемент списка содержит
    одну (list)
    """
    print("Finding vacancies...")
    vacancies = []
    response = get_request(domain)
    soup = BeautifulSoup(response.text, 'html.parser')

    for word in SEARCH_WORDS: 
        # Находим все блоки, содержащие шаблоны
        vacancy_blocks = html.fromstring(response.text).xpath("//*[contains(text(), '{0}')]".format(word))
        if vacancy_blocks: 
            for tag in vacancy_blocks:
                text_to_append = ''
                iters = 0
                # Ищем текст по родительским блокам до тех пор,
                # пока не захватится следующая вакансия (то есть, пока
                # слово "Требование", например, не будет содержаться в одном блоке дважды)
                while text_to_append.count(word) < 2 and iters < MAX_ITERS:
                    tag = tag.getparent() 
                    if len(tag):
                        vacancy_block = html.tostring(tag, encoding='utf-8').decode('utf-8')
                        vacancy_text = BeautifulSoup(vacancy_block, "lxml").text
                        if vacancy_text:
                            vacancy_text = " ".join(vacancy_text.split())
                            if vacancy_text.count(word) < 2:
                                text_to_append = vacancy_text
                    iters += 1
                # Название вакансии возьмем как минимальное из всего текста, 
                # что идет до ключевых слов.
                # Пример: из строки "Менеджер по продажам, опыт работы 1 год, требования:..."
                # останется "Менеджер по продажам, " 
                vacancy_slice = lambda part_word: text_to_append[:text_to_append.find(part_word)]
                vacancy = min(vacancy_slice(SEARCH_WORDS[0]), vacancy_slice(SEARCH_WORDS[1]), \
                              vacancy_slice(SEARCH_WORDS[2]))

                href = find_content_around(response, vacancy, 'href=\".*\"') 
                if href:
                    href = href.replace('href=', '').replace('\"', '')

                date = find_content_around(response, vacancy, DATE_REGEX, MAX_ITERS=3) 
                # Разделение текста по слову "Требования"
                requirements = text_to_append.partition('Требования')[2]
                experience = re.search(re.compile(WORK_EXPERIENCE, re.I), text_to_append)
                if experience:
                    experience = experience.group(0)
                else:
                    experience = ''
                # Если требований в вакансии нет, то берем все, кроме опыта работы и названия вакансии
                if not requirements:
                    requirements = text_to_append.replace(vacancy, '').replace(experience, '')

                vacancies.append(
                    {'vacancy': vacancy,
                    'requirements': requirements,
                    'experience': experience,
                    'link': href,
                    'date': date
                    })
            return vacancies