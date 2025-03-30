import requests
from bs4 import BeautifulSoup
import re
import time
import json

def send_vacancy_response(resume_hash: str, vacancy_id: str, my_letter: str, headers: dict, cookies: dict) -> int:
    """
    Отправляет отклик на вакансию на hh.ru с сопроводительным письмом.

    :param resume_hash: Идентификатор резюме (hash)
    :param vacancy_id: Идентификатор вакансии
    :param my_letter: Текст сопроводительного письма
    :param headers: Заголовки для запроса
    :param cookies: Куки для авторизации
    :return: HTTP статус-код ответа
    """
    url_response = "https://hh.ru/applicant/vacancy_response/popup"

    files = {
        "resume_hash": (None, resume_hash),
        "vacancy_id": (None, vacancy_id),
        "letterRequired": (None, "true"),
        "letter": (None, my_letter),
        "lux": (None, "true"),
        "ignore_postponed": (None, "true"),
        "mark_applicant_visible_in_vacancy_country": (None, "false")
    }

    response = requests.post(url_response, headers=headers, cookies=cookies, files=files)
    print(f"[Отклик] Status: {response.status_code}")
    print(f"-{response.text}")
    json.loads(response.text)






    return response.status_code
def touch_resume(resume_hash: str, headers: dict, cookies: dict) -> int:
    """
    Поднимает резюме на hh.ru по переданному resume_hash.

    :param resume_hash: Идентификатор резюме (hash)
    :param headers: Заголовки для запроса
    :param cookies: Куки для авторизации
    :return: HTTP статус-код ответа
    """
    url_touch = "https://hh.ru/applicant/resumes/touch"

    # Поля формы для запроса
    touch_files = {
        "resume": (None, resume_hash),
        "undirectable": (None, "true")
    }

    response = requests.post(url_touch, headers=headers, cookies=cookies, files=touch_files)
    print(f"[Поднятие резюме] Status: {response.status_code}")
    return response.status_code
def get_vacancy_ids(url: str, headers: dict, cookies: dict) -> list:
    """
    Делает GET-запрос к hh.ru и возвращает список ID вакансий со страницы поиска.

    :param url: Ссылка на страницу поиска вакансий
    :param headers: Заголовки запроса
    :param cookies: Куки авторизации
    :return: Список ID вакансий
    """
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, "html.parser")

    vacancy_links = soup.find_all("a", href=re.compile(r"/vacancy/\d+"))
    vacancy_ids = []

    for link in vacancy_links:
        match = re.search(r"/vacancy/(\d+)", link["href"])
        if match:
            vacancy_ids.append(match.group(1))

    return list(set(vacancy_ids))


url="<link>"
pages="<number>"
resume_hash="<id_resume>"  #dsdsd59ff04cefdfds32d1f6d6c73563035  <- https://hh.ru/resume/|dsdsd59ff04cefdfds32d1f6d6c73563035|
my_letter = (
    "Здравствуйте!\n\n"
    "Я выражаю искренний интерес к возможности присоединиться к вашей компании. "
    "Ознакомившись с деятельностью вашей организации, уверен(а), что мой опыт и навыки могут быть полезны вашей команде.\n\n"
    "Я всегда стремлюсь к профессиональному развитию и готов(а) осваивать новое. "
    "Уверена, что ваша компания предоставляет отличные возможности для роста, обучения и самореализации. "
    "Буду рад(а) стать частью вашей команды и внести свой вклад в достижение общих целей.\n\n"
    "С уважением,\n"
    "Имя Отчество\n"
    "📞 <норме>\n"
    "📧 <почта>"
)
# Авторизационные данные
hhtoken = "<token hhtoken>"
hhul = "<token hhul>"
crypted_id = "<token crypted_id>"
xsrf = "<token xsrf>"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://hh.ru/vacancy/118797963?from=applicant_recommended&hhtmFrom=main",
    "Origin": "https://hh.ru",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.5",
    "X-Requested-With": "XMLHttpRequest",
    "X-HHTMFrom": "main",
    "X-HHTMSource": "vacancy",
    "X-XsrfToken": xsrf
}

cookies = {
    "hhtoken": hhtoken,
    "hhul": hhul,
    "crypted_id": crypted_id,
    "_xsrf": xsrf
}



spis_vacansy=[]

for i in range(pages):
    spis_vacansy+=get_vacancy_ids(url+f"&page={i}", headers, cookies)

print(spis_vacansy)
print(len(spis_vacansy))



for i in get_vacancy_ids(url, headers, cookies):
    print(1)
    send_vacancy_response(resume_hash, i, my_letter, headers, cookies)
    time.sleep(3)

touch_resume(resume_hash, headers, cookies) # поднятие резюме