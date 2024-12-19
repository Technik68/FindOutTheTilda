import tkinter as tk
from tkinter import messagebox, filedialog, Scrollbar, Text, Frame, Label, Button, Checkbutton, BooleanVar
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from openpyxl import Workbook

input_file = ''
output_file = ''
sort_https_first = False  # Переменная для сортировки

def is_tilda_site(html):
    try:
        soup = BeautifulSoup(html, 'lxml')

        if soup.find('meta', {'name': 'generator', 'content': 'Tilda'}):
            return True
        if soup.find('link', {'href': lambda x: x and 'tildacdn.com' in x}):
            return True
        if soup.find_all(class_=lambda x: x and x.startswith('t-')):
            return True
        if 'This site was made on Tilda' in html:
            return True
        return False
    except Exception as e:
        return None

def is_wordpress_site(html):
    try:
        soup = BeautifulSoup(html, 'lxml')

        if soup.find('meta', {'name': 'generator', 'content': 'WordPress'}):
            return True
        if 'wp-content' in html:
            return True
        return False
    except Exception as e:
        return None

def is_wix_site(html):
    try:
        soup = BeautifulSoup(html, 'lxml')

        # Проверка на наличие метатегов или ссылок, относящихся к Wix
        if 'wix.com' in html or soup.find('meta', {'name': 'generator', 'content': 'Wix'}):
            return True
        return False
    except Exception as e:
        return None

def is_creatium_site(html):
    try:
        soup = BeautifulSoup(html, 'lxml')

        # Проверка на наличие метатегов или ссылок, относящихся к Creatium
        if 'creatium.com' in html or soup.find('meta', {'name': 'generator', 'content': 'Creatium'}):
            return True
        return False
    except Exception as e:
        return None

def is_bitrix24_site(html):
    try:
        soup = BeautifulSoup(html, 'lxml')

        # Проверка на наличие метатегов или ссылок, относящихся к Bitrix24
        if 'bitrix24' in html or soup.find('meta', {'name': 'generator', 'content': 'Bitrix24'}):
            return True
        return False
    except Exception as e:
        return None

def get_site_name(html):
    try:
        soup = BeautifulSoup(html, 'lxml')  # Используем lxml для парсинга
        title = soup.find('title')
        return title.text.strip() if title else "Название не найдено"
    except Exception as e:
        return "Ошибка при получении названия"

async def fetch_url(session, url):
    try:
        async with session.get(url) as response:
            html = await response.text()
            return url, html
    except Exception as e:
        return url, None

async def check_all_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

def check_sites():
    urls = entry_urls.get("1.0", tk.END).splitlines()
    results_text.delete(1.0, tk.END)

    urls = [url.strip() for url in urls if url.strip()]

    if not urls:
        messagebox.showerror("Ошибка", "Не введены URL.")
        return

    if only_http_var.get():
        urls = [url for url in urls if url.startswith("http://")]
    elif only_https_var.get():
        urls = [url for url in urls if url.startswith("https://")]

    async def process_urls():
        results = []
        site_data = []
        responses = await check_all_urls(urls)

        for url, html in responses:
            if html is None:
                status = "Ошибка проверки"
                site_name = "Ошибка при получении названия"
                is_tilda = False
                is_wordpress = False
                is_wix = False
                is_creatium = False
                is_bitrix24 = False
            else:
                site_name = get_site_name(html)
                is_tilda = is_tilda_site(html)
                is_wordpress = is_wordpress_site(html)
                is_wix = is_wix_site(html)
                is_creatium = is_creatium_site(html)
                is_bitrix24 = is_bitrix24_site(html)

                if is_tilda:
                    status = "✅ На Tilda"
                elif is_wordpress:
                    status = "📝 На WordPress"
                elif is_wix:
                    status = "🌐 На Wix"
                elif is_creatium:
                    status = "⚙️ На Creatium"
                elif is_bitrix24:
                    status = "💼 На Битрикс24"
                else:
                    status = "✍️ Рукописный сайт"

                if only_tilda_var.get() and not is_tilda:
                    continue

            site_data.append((url, site_name, status))

            result_line = f"{'-' * 60}\n"
            result_line += f"📍 URL: {url}\n"
            result_line += f"🏷 Название сайта: {site_name}\n"
            result_line += f"✅ Статус: {status}\n"
            result_line += f"{'-' * 60}\n\n"

            results_text.insert(tk.END, result_line)
            results.append(result_line)

        # Сортировка по протоколу (https, http)
        if sort_https_first_var.get():
            site_data.sort(key=lambda x: (x[0].startswith("https://"), x[0]))

        # Формирование результатов в Excel
        if site_data:
            create_excel_report(site_data)

    asyncio.run(process_urls())

def bind_ctrl_v(event):
    event.widget.event_generate("<<Paste>>")

def select_input_file():
    global input_file
    input_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if input_file:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                urls = f.read().splitlines()
                entry_urls.delete('1.0', tk.END)
                entry_urls.insert(tk.END, "\n".join(urls))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

def select_output_file():
    global output_file
    output_file = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text files", "*.txt")])
    if not output_file:
        output_file = ''

def create_excel_report(site_data):
    # Создание нового Excel-файла
    wb = Workbook()
    ws = wb.active

    # Задаем имена столбцов
    ws.append(["Компания URL", "Название сайта", "Статус"])

    # Заполнение данными
    for url, site_name, status in site_data:
        ws.append([url, site_name, status])

    # Сохранение Excel-файла
    try:
        excel_file = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                  filetypes=[("Excel files", "*.xlsx")])
        if excel_file:
            wb.save(excel_file)
            messagebox.showinfo("Успех", f"Отчет успешно сохранен в: {excel_file}")
        else:
            messagebox.showinfo("Отмена", "Сохранение Excel отменено.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить отчет: {e}")

# Визуальный интерфейс приложения
root = tk.Tk()
root.title('🔍 Проверка сайтов на Tilda, Wix, WordPress, Creatium и Битрикс24')

root.configure(bg="#E2E3DD")

# Главный фрейм для организации интерфейса
main_frame = Frame(root, bg="#E2E3DD")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Левая часть с кнопками и чекбоксами
left_frame = Frame(main_frame, bg="#E2E3DD")
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Кнопки для выбора входного и выходного файлов
Button(left_frame, text="📂 Выбрать входной файл", command=select_input_file, bg="#C5C5B9", font=('Helvetica', 12)).pack(fill=tk.X, pady=5)
Button(left_frame, text="💾 Выбрать выходной файл", command=select_output_file, bg="#A09F8D", font=('Helvetica', 12)).pack(fill=tk.X, pady=5)

# Чекбоксы
only_tilda_var = BooleanVar()
Checkbutton(left_frame, text="Показывать только сайты на Tilda", variable=only_tilda_var, font=('Helvetica', 12), bg="#E2E3DD", anchor="w").pack(fill=tk.X, pady=5)

only_http_var = BooleanVar()
Checkbutton(left_frame, text="Показывать только HTTP", variable=only_http_var, font=('Helvetica', 12), bg="#E2E3DD", anchor="w").pack(fill=tk.X, pady=5)

only_https_var = BooleanVar()
Checkbutton(left_frame, text="Показывать только HTTPS", variable=only_https_var, font=('Helvetica', 12), bg="#E2E3DD", anchor="w").pack(fill=tk.X, pady=5)

# Новый чекбокс для сортировки
sort_https_first_var = BooleanVar()
Checkbutton(left_frame, text="Сортировать: сначала HTTPS, потом HTTP", variable=sort_https_first_var, font=('Helvetica', 12), bg="#E2E3DD", anchor="w").pack(fill=tk.X, pady=5)

# Кнопка для проверки сайтов
Button(left_frame, text="✅ Проверить", command=check_sites, font=('Helvetica', 14), bg="#90caf9", fg="white").pack(fill=tk.X, pady=10)

# Правая часть с текстовыми полями
right_frame = Frame(main_frame, bg="#E2E3DD")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Поле для ввода URL
Label(right_frame, text="Введите URL в блок через новую строку:", font=('Helvetica', 14), bg="#E2E3DD", fg="#31312F").pack(anchor="w", pady=5)
entry_urls = Text(right_frame, height=10, font=('Courier', 12), wrap=tk.WORD, fg="#31312F", bg="#E5E1D8")
entry_urls.pack(fill=tk.BOTH, padx=10, pady=5)

# Разделитель
Label(right_frame, text="Результаты проверки:", font=('Helvetica', 14), bg="#E2E3DD", fg="#31312F").pack(anchor="w", pady=5)

# Блок для вывода результатов
results_text = Text(right_frame, height=20, font=('Courier', 12), wrap=tk.WORD, fg="#31312F", bg="#E5E1D8")
results_text.pack(fill=tk.BOTH, padx=10, pady=5)

root.mainloop()
