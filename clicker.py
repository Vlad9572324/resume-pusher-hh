import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
from glom import glom
import json
from tabulate import tabulate
import time
from datetime import datetime, timedelta

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

def send_vacancy_response(
    resume_hash: str,
    vacancy_id: str,
    my_letter: str,
    headers: dict,
    cookies: dict,
    response_number: int = None,
    total_responses: int = None
) -> int:
    """
    Отправляет отклик на вакансию на hh.ru с сопроводительным письмом и красиво выводит информацию.
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

    if response.status_code != 200:
        print(f"❌ Ошибка отправки отклика. Код: {response.status_code}")
        print(f"Ответ текст: {response.text[:80]}")
        return response.status_code, response.text

    try:
        parsed = response.json()
    except json.JSONDecodeError:
        print("❌ Ошибка: некорректный JSON в ответе.")
        return response.status_code, response.text

    # Извлечение полей
    info = {
        "💼 ID вакансии": glom(parsed, "responseStatus.shortVacancy.vacancyId", default=None),
        "📌 Название": glom(parsed, "responseStatus.shortVacancy.name", default=None),
        "🏢 Компания": glom(parsed, "responseStatus.shortVacancy.company.name", default=None),
        "🗺️ Город": glom(parsed, "responseStatus.shortVacancy.area.name", default=None),
        "🏠 Адрес": glom(parsed, "responseStatus.shortVacancy.address.displayName", default=None),
        "💰 Зарплата от": glom(parsed, "responseStatus.shortVacancy.compensation.from", default=None),
        "💰 Зарплата до": glom(parsed, "responseStatus.shortVacancy.compensation.to", default=None),
        "💱 Валюта": glom(parsed, "responseStatus.shortVacancy.compensation.currencyCode", default=None),
        "🪙 До вычета налогов": glom(parsed, "responseStatus.shortVacancy.compensation.gross", default=None),
        "📆 Дата публикации": glom(parsed, "responseStatus.shortVacancy.publicationTime.$", default=None),
        "📅 Опыт": glom(parsed, "responseStatus.shortVacancy.workExperience", default=None),
        "⏰ График": glom(parsed, "responseStatus.shortVacancy.@workSchedule", default=None),
        "👷 Тип занятости": glom(parsed, "responseStatus.shortVacancy.employmentForm", default=None),
        "🧑‍💼 Менеджер": f"{glom(parsed, 'responseStatus.shortVacancy.employerManager.@firstName', default='')} {glom(parsed, 'responseStatus.shortVacancy.employerManager.@lastName', default='')}".strip(),
        "🌐 Ссылка (ПК)": glom(parsed, "responseStatus.shortVacancy.links.desktop", default=None),
        "📱 Ссылка (моб)": glom(parsed, "responseStatus.shortVacancy.links.mobile", default=None),
        "✅ Отклик отправлен": glom(parsed, "responseStatus.negotiations.topicList.0.responded", default=None),
        "📩 Есть письмо": glom(parsed, "responseStatus.negotiations.topicList.0.hasResponseLetter", default=None),
        "👁️ Просмотрено": glom(parsed, "responseStatus.negotiations.topicList.0.viewedByOpponent", default=None),
        "📬 Непрочитано работодателем": glom(parsed, "responseStatus.negotiations.topicList.0.conversationUnreadByEmployerCount", default=None),
        "🧵 Чат в архиве": glom(parsed, "responseStatus.negotiations.topicList.0.chatIsArchived", default=None),
        "📛 Можно отклонить?": glom(parsed, "responseStatus.negotiations.topicList.0.declineByApplicantAllowed", default=None),
        "🎯 Стандартная вакансия": glom(parsed, "responseStatus.shortVacancy.vacancyProperties.calculatedStates.HH.standard", default=None),
        "🔒 Компания проверена": glom(parsed, "responseStatus.shortVacancy.company.@trusted", default=None),
        "🧩 Принимает неполные резюме": glom(parsed, "responseStatus.shortVacancy.acceptIncompleteResumes", default=None),
        "📮 Возможен чат": glom(parsed, "responseStatus.shortVacancy.chatWritePossibility", default=None),
    }

    # Удаляем пустые значения
    info = {k: v for k, v in info.items() if v not in [None, "", []]}

    # Красивый вывод
    print("\n" + "📋 Информация о вакансии".center(70, "─"))
    print(f"Ответ: {response.status_code}")
    print(f"Ответ текст: {response.text[:80]}")
    print(tabulate(info.items(), headers=["🧾 Поле", "📌 Значение"], tablefmt="fancy_grid"))

    # Доп. строка с номером отклика
    if response_number and total_responses:
        print(f"\n➡️ Отклик {response_number}/{total_responses} на вакансию ID: {info.get('💼 ID вакансии')}")
    else:
        print(f"\n✅ Успешно откликнулись на вакансию ID: {info.get('💼 ID вакансии')}")

    # Ссылка на вакансию
    if "🌐 Ссылка (ПК)" in info:
        print(f"🔗 {info['🌐 Ссылка (ПК)']}")

    return response.status_code, response.text

def get_vacancy_ids(url, headers, cookies,numb):
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, "html.parser")

    vacancy_links = soup.find_all("a", href=re.compile(r"/vacancy/\d+"))
    vacancy_ids = set()

    for link in vacancy_links:
        match = re.search(r"/vacancy/(\d+)", link["href"])
        if match:
            vacancy_ids.add(match.group(1))

    print(f"🔎 С {numb} страницы получено {len(vacancy_ids)} вакансий")

    return list(vacancy_ids)


# Основные параметры
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
    "<Имя Отчество>\n"
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

all_vacancies = set()



# Настройка интервалов
resume_lift_interval = timedelta(hours=4, minutes=10)
vacancy_response_interval = timedelta(hours=2)

# Время последнего действия
last_resume_lift = datetime.min
last_response_attempt = datetime.min

while True:
    now = datetime.now()

    # 🟡 Поднятие резюме раз в 4 часа 10 минут
    if now - last_resume_lift >= resume_lift_interval:
        print(f"\n🕓 {now.strftime('%H:%M:%S')} — Поднимаю резюме...\n")
        touch_resume(resume_hash, headers, cookies)
        last_resume_lift = now

    # 🔁 Попытка откликнуться раз в 2 часа
    if now - last_response_attempt >= vacancy_response_interval:
        print(f"\n🕑 {now.strftime('%H:%M:%S')} — Начинаю откликаться на вакансии...\n")

        all_vacancies = set()

        # Получение вакансий
        for i in range(10):  # или больше страниц
            current_page_url = f"{url}&page={pages}"
            vacancies = get_vacancy_ids(current_page_url, headers, cookies, i)
            all_vacancies.update(vacancies)
            time.sleep(2)

        print(f"\n🚩 Всего вакансий получено: {len(all_vacancies)}\n")

        for idx, vacancy_id in enumerate(all_vacancies, 1):
            print(f"➡️ Отклик {idx}/{len(all_vacancies)} на вакансию ID: {vacancy_id}")
            status_code, response_text = send_vacancy_response(resume_hash, vacancy_id, my_letter, headers, cookies)

            if status_code != 200:
                print(f"❌ Ошибка отправки отклика. Код: {status_code}")
                print(f"Ответ текст: {response_text}")

                # Пропускаем, если требуется тест
                if "test-required" in response_text or "unknown" in response_text:
                    print("⏩ Вакансия требует прохождения теста — пропускаю.\n")
                    continue
                else:
                    print(f"⚠️ Ответ от сервера: {status_code}. Повторная попытка через 2 часа.")
                    break  # Прерываем цикл и ждём 2 часа

            time.sleep(3)

        print("\n✅ Все отклики (кроме ошибок) отправлены.")
        last_response_attempt = now

    # 💤 Пауза между циклами
    time.sleep(60)  # проверка каждые 60 секунд