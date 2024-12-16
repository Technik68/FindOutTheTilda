import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def is_tilda_site(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверяет, был ли успешным запрос (статус 200)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск ключевых признаков Tilda
        if soup.find('meta', {'name': 'generator', 'content': 'Tilda'}):
            return True
        if soup.find('link', {'href': lambda x: x and 'tildacdn.com' in x}):
            return True
        if soup.find_all(class_=lambda x: x and x.startswith('t-')):
            return True
        if 'This site was made on Tilda' in response.text:
            return True
        return False
    except Exception as e:
        print(f"Ошибка при проверке {url}: {e}")
        return None  # Возвращаем None, если возникла ошибка

def get_site_name(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        return title.text.strip() if title else "Название не найдено"
    except Exception as e:
        print(f"Ошибка при получении названия сайта для {url}: {e}")
        return "Ошибка при получении названия"

def check_sites_from_file(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Файл {input_file} не найден. Проверьте путь.")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            urls = [line.strip() for line in infile.readlines() if line.strip()]

        results = []
        for url in urls:
            site_name = get_site_name(url)
            is_tilda = is_tilda_site(url)
            if is_tilda is None:
                status = "Ошибка проверки"
            elif is_tilda:
                status = "На Tilda"
            else:
                status = "Не на Tilda"
            results.append(f"{site_name} - {url} - {status}")

        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write("\n".join(results))

        print(f"Проверка завершена. Результаты сохранены в {output_file}")
    except Exception as e:
        print(f"Ошибка при обработке файлов: {e}")

# Файлы ввода и вывода
input_file = 'input_urls.txt'  # Файл со списком URL
output_file = 'output_results.txt'  # Файл для сохранения результатов

# Запуск проверки
check_sites_from_file(input_file, output_file)
