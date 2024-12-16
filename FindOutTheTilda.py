import tkinter as tk
from tkinter import messagebox, filedialog, Scrollbar, Text
import requests
from bs4 import BeautifulSoup


input_file = ''
output_file = ''


def is_tilda_site(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

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
        return None


def get_site_name(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        return title.text.strip() if title else "Название не найдено"
    except Exception as e:
        return "Ошибка при получении названия"


def check_sites():
    urls = entry_urls.get("1.0", tk.END).splitlines()
    results_text.delete(1.0, tk.END)  # Очищаем блок результатов

    urls = [url.strip() for url in urls if url.strip()]

    if not urls:
        messagebox.showerror("Ошибка", "Не введены URL.")
        return

    results = []
    for url in urls:
        site_name = get_site_name(url)
        is_tilda = is_tilda_site(url)

        if is_tilda is None:
            status = "Ошибка проверки"
        elif is_tilda:
            status = "✅ На Tilda"
        else:
            status = "❌ Не на Tilda"

        result_line = f"{'-' * 50}\n"
        result_line += f"📍 URL: {url}\n"
        result_line += f"🏷 Название сайта: {site_name}\n"
        result_line += f"✅ Статус: {status}\n"
        result_line += f"{'-' * 50}\n\n"

        results_text.insert(tk.END, result_line)
        results.append(result_line)

    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(results))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить в файл: {e}")


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


# Визуальный интерфейс приложения
root = tk.Tk()
root.title('Проверка сайтов на Tilda')

tk.Label(root, text="Введите URL в блок через новую строку:").pack()

# Поле для ввода URL
entry_urls = Text(root, height=10)
entry_urls.pack(fill=tk.BOTH, padx=10, pady=10)

# Привязываем сочетание Ctrl+V
entry_urls.bind("<Control-v>", bind_ctrl_v)

# Кнопки для выбора входного и выходного файла
tk.Button(root, text="Выбрать входной файл", command=select_input_file).pack(pady=5)
tk.Button(root, text="Выбрать выходной файл", command=select_output_file).pack(pady=5)

# Кнопка для проверки сайтов
tk.Button(root, text="Проверить", command=check_sites).pack(pady=10)

# Блок для вывода результатов
tk.Label(root, text="Результаты проверки:").pack()

results_text = Text(root, height=20, font=('Courier', 12))
results_text.pack(fill=tk.BOTH, padx=10, pady=10)

root.mainloop()
