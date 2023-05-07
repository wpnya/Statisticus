import customtkinter as ctk
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

login = "yourlogin"
password = "yourpassword"

options = webdriver.ChromeOptions()
window_size = "1600,900"

options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
options.add_argument("--headless")
options.add_argument("--window-size=%s" % window_size)
s = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(
    service=s,
    options=options
)


def start():
    try:
        vkid_link()
        searching_audios()
        sorting_performers()
        final_text()
    except Exception as ex:
        textbox.delete("0.0", "end")
        textbox.insert("end", "Такого аккаунта нет")


def vkid_link():
    i = 0
    while True:
        vkid = str(app.entry_id.get())
        if not vkid.isdigit():
            driver.get("https://regvk.com/id/")
            id_input = driver.find_element(By.ID, "enter")
            id_input.send_keys(vkid)
            driver.find_element(By.NAME, "button").click()
            if len(driver.find_elements(By.XPATH, "//*[contains(text(), 'ID пользователя:')]")) != 0:
                info = driver.find_element(By.XPATH, "//*[contains(text(),'ID пользователя:')]").text
                origin_id = info.split(":")[1].strip()
                vkid = origin_id
                print("Аккаунт найден", vkid)
                i = 0
                break
            else:
                textbox.insert("end", "Такого аккаунта нет")
                i += 1
                break
        else:
            print("Аккаунт найден")
            i = 0
            break

    if i == 0:
        print(vkid)
        link = "https://vk.com/audios" + vkid
        driver.get(link)
        driver.maximize_window()
        if len(driver.find_elements(By.ID, "index_email")) != 0:
            email_input = driver.find_element(By.ID, "index_email")
            email_input.clear()
            email_input.send_keys(login)
            email_input.submit()
            time.sleep(2)

            captcha()

            pass_input = driver.find_element(By.NAME, "password")
            pass_input.click()
            pass_input.clear()
            pass_input.send_keys(password)
            pass_input.submit()
            time.sleep(2)


def captcha_settings():
    if len(driver.find_elements(By.CLASS_NAME, "vkc__Captcha__image")) != 0:
        print("Капча")
        with open('captcha.png', 'wb') as file:
            file.write(driver.find_element(By.CLASS_NAME, "vkc__Captcha__image").screenshot_as_png)
        captcha_window = ctk.CTkInputDialog(text="Введите код с картинки", title="reCapcha")
        captcha_image = ctk.CTkImage(dark_image=Image.open("captcha.png"), size=(208, 100))
        captcha_window_label = ctk.CTkLabel(master=captcha_window, text="", image=captcha_image)
        captcha_window_label.grid(row=3, column=0, padx=(120, 0))
        captcha = captcha_window.get_input()
        captcha_input = driver.find_element(By.CLASS_NAME, "vkc__TextField__input")
        captcha_input.click()
        captcha_input.send_keys(captcha)
        captcha_input.submit()
        time.sleep(2)


def captcha():
    while True:
        if len(driver.find_elements(By.CLASS_NAME, "vkc__Captcha__image")) != 0:
            captcha_settings()
        else:
            break


def searching_audios():
    if len(driver.find_elements(By.CLASS_NAME, "MusicOwnerCell__description")) != 0:
        print("Ищу музыку")
        info = driver.find_element(By.CLASS_NAME, "MusicOwnerCell__description").text
        audios_amount = info.split()[0].strip()
        if int(audios_amount) >= 80:
            x, y = divmod(int(audios_amount), 80)
            for i in range(x):
                time.sleep(2)
                driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
            driver.find_element(By.CLASS_NAME, "stl_active").click()
        else:
            pass
    else:
        textbox.insert("end", "Музыка скрыта или удалена")


def sorting_performers():
    performers = []
    musians_info = driver.find_elements(By.CLASS_NAME, "audio_row__performers")
    for i in musians_info:
        performers.append(i.text)

    my_dic = {}
    for item in performers:
        items = item.replace(' feat. ', ', ').split(', ')
        for element in items:
            if element not in my_dic:
                my_dic[element] = 1
            else:
                my_dic[element] += 1
    sorted_dic = {}
    sorted_keys = sorted(my_dic, key=my_dic.get, reverse=True)

    for i in sorted_keys:
        sorted_dic[i] = my_dic[i]

    final_dic = []
    for key, value in sorted_dic.items():
        final_dic.append(f'{key}: ' f'{value}')
    return final_dic


def final_text():
    try:
        final_dic = sorting_performers()
        textbox.delete("0.0", "end")
        for i in range(0, 10):
            textbox.insert("end", f'{final_dic[i]}\n')
    except Exception as ex:
        if driver.find_element(By.CLASS_NAME, "AudioPlaceholder__text"):
            textbox.insert("end", "Музыка скрыта или удалена")
        else:
            textbox.insert("end", "Такого аккаунта нет")


app = ctk.CTk()
app.geometry("460x500")

app.title("Statisticus")
app.resizable(False, False)

app.logo = ctk.CTkImage(dark_image=Image.open("logo.png"), size=(450, 200))
app.logo_label = ctk.CTkLabel(master=app, text="", image=app.logo)
app.logo_label.grid(row=0, column=0)

app.id_frame = ctk.CTkFrame(master=app, fg_color="transparent")
app.id_frame.grid(row=1, column=0, padx=(20, 20), sticky="nsew")

app.entry_id = ctk.CTkEntry(master=app.id_frame, width=300, border_color="grey")
app.entry_id.grid(row=0, column=0, padx=(0, 20))

app.btn = ctk.CTkButton(master=app.id_frame, text="Find", width=100, command=start)
app.btn.grid(row=0, column=1)

textbox = ctk.CTkTextbox(master=app, width=200, bg_color="red", height=200, corner_radius=0)
textbox.grid(row=2, column=0, pady=(35, 0))

app.mainloop()
