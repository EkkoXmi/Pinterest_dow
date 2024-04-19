import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
from PIL import ImageTk, Image
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import os
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC

def download_images(keyword, scroll_count, save_directory, format_var):
    url = 'https://www.pinterest.com/'
    driver = webdriver.Chrome()
    driver.get(url)
    driver.maximize_window()
    driver.implicitly_wait(5)
    link_explore = driver.find_element(By.CSS_SELECTOR, ".tBJ.dyH.iFc.sAJ.X8m.zDA.UK7.H2s")
    link_explore.click()
    search_input = driver.find_element(By.NAME, "searchBoxInput")
    search_input.send_keys(keyword)
    search_input.send_keys(Keys.ENTER)
    downloaded_image_count = 0
    image_urls = []
    wait = WebDriverWait(driver, 10)
    current_scroll = 0
    while current_scroll <= scroll_count:
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        current_scroll += 1
        time.sleep(5)
        try:
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "img")))
        except TimeoutException:
            print("等待圖片加載超時")
            break
        images = driver.find_elements(By.TAG_NAME, "img")
        for image in images:
            try:
                image_url = image.get_attribute("src")
                image_url = image_url.replace("236x", "originals")
                image_urls.append(image_url)
                image_filename = os.path.join(save_directory, f"image{downloaded_image_count}.{format_var.get().lower()}")
                with open(image_filename, 'wb') as img_file:
                    img_file.write(requests.get(image_url).content)
                downloaded_image_count += 1
                print(f"已下載圖片: {image_filename}")
            except (StaleElementReferenceException, NoSuchElementException):
                images = driver.find_elements(By.TAG_NAME, "img")
    print("所有圖片已經下載完成！")
    with open(os.path.join(save_directory, "image_urls.txt"), "w") as f:
        for url in image_urls:
            f.write(url + "\n")
    driver.quit()
    messagebox.showinfo("下載完成", "所有圖片已經下載完成！")

def start_download():
    keyword = entry_keyword.get()
    scroll_text = entry_scroll.get()
    if not keyword or keyword.strip() == "請輸入想搜尋的圖片":
        messagebox.showerror("錯誤", "請輸入搜尋關鍵字！")
    elif not scroll_text.isdigit() or int(scroll_text) < 0:
        messagebox.showerror("錯誤", "請輸入有效的滾動次數！")
    else:
        scroll_count = int(scroll_text)
        save_directory = choose_directory()
        if save_directory:
            download_images(keyword, scroll_count, save_directory, format_var)

def choose_directory():
    directory = filedialog.askdirectory()
    return directory

def choose_background_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        crop_and_set_background(file_path)

def crop_and_set_background(file_path):
    bg_image = Image.open(file_path)
    bg_image = bg_image.resize((512, 288))
    bg_image = bg_image.convert("RGB")
    bg_image.save("TKBG.jpg")
    bg_photo = ImageTk.PhotoImage(bg_image)
    background_label.configure(image=bg_photo)
    background_label.image = bg_photo

window = tk.Tk()
style = ttk.Style()

style.configure('A.TButton', foreground='black', background='white', font=('微軟正黑體', 10), width=4, height=10)
style.configure('B.TButton', foreground='black', background='white', font=('微軟正黑體', 10), width=6.5, height=10)

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_width = 512
window_height = 288

x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

window.geometry(f"{window_width}x{window_height}+{x}+{y}")
default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="微軟正黑體")
window.option_add("*Font", default_font)
window.resizable(False, False)
window.title("Pinterest 圖片下載程式")
window.iconbitmap('LOGO.ico')

bg_image = Image.open('TKBG.jpg')
bg_image = bg_image.resize((512, 288))
bg_photo = ImageTk.PhotoImage(bg_image)

background_label = tk.Label(window, image=bg_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
label_keyword = tk.Label(window, text="關鍵字:", bg="white")
label_keyword.grid(row=0, column=0, padx=10, pady=5, sticky='w')

keyword_text = "請輸入想搜尋的圖片"
entry_keyword = tk.Entry(window, width=20)
entry_keyword.insert(0, keyword_text)
entry_keyword.bind("<FocusIn>", lambda event: entry_keyword.delete(0, "end"))
entry_keyword.grid(row=0, column=1, padx=10, pady=5, sticky='w')

label_scroll = tk.Label(window, text="滾動次數:", bg="white")
label_scroll.grid(row=1, column=0, padx=10, pady=5, sticky='w')
scroll_text = "建議1~10次"
entry_scroll = tk.Entry(window, width=10)
entry_scroll.insert(0, scroll_text)
entry_scroll.bind("<FocusIn>", lambda event: entry_scroll.delete(0, "end"))
entry_scroll.grid(row=1, column=1, padx=10, pady=5, sticky='w')

format_var = tk.StringVar()
format_choices = ["jpg", "png"]
format_dropdown = ttk.Combobox(window, values=format_choices, textvariable=format_var, state="readonly", width=4)
format_dropdown.set(format_choices[0])
format_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky='w')

button_start = ttk.Button(window, text="下載", command=start_download, style='A.TButton')
button_start.grid(row=2, column=0, padx=10, pady=5, rowspan=2, sticky='w')

def choose_background_image():
    response = messagebox.askokcancel("建議","建議選擇尺寸16 : 9的背景圖片")
    if response:
        file_path = filedialog.askopenfilename()
        if file_path:
            crop_and_set_background(file_path)
button_change_bg = ttk.Button(window, text="更換背景", style='B.TButton', command=choose_background_image)
button_change_bg.place(relx=0.0, rely=1.0, anchor='sw')

def show_author():
    messagebox.showinfo("關於", "作者 : 趙子文\n版本:  ver.9\n使用自動化瀏覽器模擬操作\n方便大量下載圖片")
btn_about = ttk.Button(window, text="關於", style='A.TButton', command=show_author)
btn_about.place(relx=1.0, rely=1.0, anchor='se')

window.mainloop()
