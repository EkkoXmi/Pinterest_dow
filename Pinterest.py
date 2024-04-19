import tkinter as tk# 匯入 tkinter 模組
from tkinter import ttk, font, messagebox, filedialog# 匯入 ttk、font、messagebox、filedialog 模組
from PIL import ImageTk, Image# 匯入 ImageTk、Image 模組
import time# 匯入 time 模組
from selenium import webdriver# 匯入 selenium 模組
from selenium.webdriver.support.ui import WebDriverWait# 匯入 WebDriverWait 模組
from selenium.webdriver.common.by import By# 匯入 By 模組
from selenium.webdriver.common.keys import Keys# 匯入 Keys 模組
import requests# 匯入 requests 模組
import os# 匯入 os 模組
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException# 匯入例外狀況模組
from selenium.webdriver.support import expected_conditions as EC# 匯入 expected_conditions 模組

# 下載圖片的函數
def download_images(keyword, scroll_count, save_directory, format_var):
    # 設定要爬取的網址
    url = 'https://www.pinterest.com/'
    # 設定 Chrome 為 webdriver
    driver = webdriver.Chrome()
    # 開啟網頁
    driver.get(url)

    # 視窗最大化
    driver.maximize_window()# 視窗最大化
    # 建立網頁的開啟時間
    driver.implicitly_wait(5)# 等待 5 秒
    # 開啟網頁，找到探索連結並點擊
    link_explore = driver.find_element(By.CSS_SELECTOR, ".tBJ.dyH.iFc.sAJ.X8m.zDA.UK7.H2s")
    # 點擊探索連結
    link_explore.click()

    # 找到搜尋框並輸入要搜尋的資訊
    search_input = driver.find_element(By.NAME, "searchBoxInput")# 找到搜尋框
    search_input.send_keys(keyword)# 輸入搜尋關鍵字

    # 模擬按下 Enter 鍵執行搜尋
    search_input.send_keys(Keys.ENTER)# 按下 Enter 鍵執行搜尋

    # 初始化已下載圖片數量
    downloaded_image_count = 0# 已下載圖片數量

    # 初始化圖片網址列表
    image_urls = []

    # 使用顯式等待等待新圖片加載
    wait = WebDriverWait(driver, 10)# 設定等待時間為 10 秒
    
    # 開始滾動
    current_scroll = 0# 目前滾動次數
    while current_scroll <= scroll_count: # 持續滾動直到滾動次數達到 scroll_count
        driver.execute_script("window.scrollBy(0, window.innerHeight);")# 執行 JavaScript 指令，模擬滾動視窗
        current_scroll += 1 # 目前滾動次數加 1
        
        # 等待下載時間
        time.sleep(5)  # 可以根據網速調整等待時間
        
        # 等待圖片加載
        try:
            # 使用顯式等待等待新圖片加載
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "img")))
        except TimeoutException:
            print("等待圖片加載超時")
            break
        
        # 抓取圖片標籤
        images = driver.find_elements(By.TAG_NAME, "img")
        
        # 下載圖片並收集圖片網址
        for image in images:
            try:
                # 獲取圖片連結
                image_url = image.get_attribute("src")
                # 將 "236x" 替換為 "originals"
                image_url = image_url.replace("236x", "originals")
                # 將圖片網址加入列表
                image_urls.append(image_url)
                # 生成圖片文件名
                image_filename = os.path.join(save_directory, f"image{downloaded_image_count}.{format_var.get().lower()}")
                # 下載圖片
                with open(image_filename, 'wb') as img_file:    # 開啟圖片檔案
                    img_file.write(requests.get(image_url).content) # 將圖片資料寫入 img_file
                # 更新已下載圖片數量
                downloaded_image_count += 1
                # 顯示已下載訊息
                print(f"已下載圖片: {image_filename}")
                # 捕捉例外狀況，避免程式中斷
            except (StaleElementReferenceException, NoSuchElementException):
                images = driver.find_elements(By.TAG_NAME, "img")

    # 顯示下載完成訊息
    print("所有圖片已經下載完成！")

    # 儲存圖片網址列表到指定路徑的檔案
    with open(os.path.join(save_directory, "image_urls.txt"), "w") as f:
        for url in image_urls:
            f.write(url + "\n")

    # 關閉瀏覽器
    driver.quit()
    
    # 顯示下載完成訊息框
    messagebox.showinfo("下載完成", "所有圖片已經下載完成！")

# 按下下載按鈕時，從Pinterest網站下載圖片到指定的儲存位置
def start_download():
    # 獲取搜尋關鍵字、滾動次數、儲存位置、圖片格式
    keyword = entry_keyword.get()
    scroll_text = entry_scroll.get()
    if not keyword or keyword.strip() == "請輸入想搜尋的圖片":
        messagebox.showerror("錯誤", "請輸入搜尋關鍵字！")
    elif not scroll_text.isdigit() or int(scroll_text) < 0:
        messagebox.showerror("錯誤", "請輸入有效的滾動次數！")
    else:   # 搜尋關鍵字、滾動次數都沒問題
        scroll_count = int(scroll_text) # 轉換成整數
        save_directory = choose_directory() # 選擇儲存位置
        if save_directory:  # 如果儲存位置沒有選擇，則不開始下載
            download_images(keyword, scroll_count, save_directory, format_var)  # 開始下載圖片

# 選擇儲存位置的函數
def choose_directory(): # 選擇儲存位置的函數
    directory = filedialog.askdirectory()   # 開啟文件選擇器，選擇儲存位置
    return directory    # 回傳選擇的儲存位置

# 選擇背景圖片的函數
def choose_background_image():  # 選擇背景圖片的函數
    file_path = filedialog.askopenfilename()  # 讓使用者選擇背景圖片文件
    if file_path:
        crop_and_set_background(file_path)  # 調用裁剪並設置背景圖片的函數

# 裁剪圖片並設置背景的函數
def crop_and_set_background(file_path): # 調用裁剪並設置背景圖片的函數
    # 開啟圖片並調整大小
    bg_image = Image.open(file_path)# 開啟圖片並調整大小
    bg_image = bg_image.resize((512, 288))  # 調整大小為 512x288
    
    # 轉換為 RGB 格式
    bg_image = bg_image.convert("RGB")# 轉換為 RGB 格式
    # 儲存裁剪後的圖片
    bg_image.save("TKBG.jpg")#   儲存裁剪後的圖片
    
    # 讀取新的背景圖片並設置為應用程式的背景
    bg_photo = ImageTk.PhotoImage(bg_image)# 讀取圖片並轉換為 PhotoImage 類別
    background_label.configure(image=bg_photo)# 設置背景圖片
    background_label.image = bg_photo  # 保持圖片的引用，避免被垃圾回收

# 建立 Tkinter 視窗與 ICON設定
window = tk.Tk()# 建立視窗
style = ttk.Style()# 設定樣式

# 設定按鈕風格
style.configure('A.TButton', foreground='black', background='white', font=('微軟正黑體', 10), width=4, height=10)   # 設定按鈕風格
style.configure('B.TButton', foreground='black', background='white', font=('微軟正黑體', 10), width=6.5, height=10) # 設定按鈕風格

# 獲取螢幕寬度和高度
screen_width = window.winfo_screenwidth()# 寬度
screen_height = window.winfo_screenheight()# 高度

# 設置視窗寬度和高度
window_width = 512
window_height = 288

# 計算視窗在螢幕中央的位置
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# 設置視窗的初始位置
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 設置視窗字體為微軟正黑體
default_font = font.nametofont("TkDefaultFont")# 獲取預設字體
default_font.configure(family="微軟正黑體")# 設置微軟正黑體為預設字體
window.option_add("*Font", default_font) # 設置所有元件的字體

# 禁止使用者調整視窗大小
window.resizable(False, False)
window.title("Pinterest 圖片下載程式")
window.iconbitmap('LOGO.ico')

# 添加背景圖片
bg_image = Image.open('TKBG.jpg')  # 更換為你的圖片路徑
bg_image = bg_image.resize((512, 288))  # 調整大小為 512x288
bg_photo = ImageTk.PhotoImage(bg_image)# 讀取圖片並轉換為 PhotoImage 類別
background_label = tk.Label(window, image=bg_photo)# 建立背景圖片標籤
background_label.place(x=0, y=0, relwidth=1, relheight=1)# 設置背景圖片位置

# 建立使用者介面元件
label_keyword = tk.Label(window, text="關鍵字:", bg="white")# 建立關鍵字標籤
label_keyword.grid(row=0, column=0, padx=10, pady=5, sticky='w')# 設置關鍵字標籤位置

keyword_text = "請輸入想搜尋的圖片"# 預設文字
entry_keyword = tk.Entry(window, width=20)# 建立搜尋框
entry_keyword.insert(0, keyword_text)  # 將預設文字放入搜尋框
entry_keyword.bind("<FocusIn>", lambda event: entry_keyword.delete(0, "end"))  # 當搜尋框被點擊時清除預設文字
entry_keyword.grid(row=0, column=1, padx=10, pady=5, sticky='w')# 設置搜尋框位置

label_scroll = tk.Label(window, text="滾動次數:", bg="white")# 建立滾動次數標籤
label_scroll.grid(row=1, column=0, padx=10, pady=5, sticky='w')# 設置滾動次數標籤位置

scroll_text = "建議1~10次"
entry_scroll = tk.Entry(window, width=10)# 建立 Entry
entry_scroll.insert(0, scroll_text)  # 將預設文字放入 Entry
entry_scroll.bind("<FocusIn>", lambda event: entry_scroll.delete(0, "end"))  # 當 Entry 被點擊時清除預設文字
entry_scroll.grid(row=1, column=1, padx=10, pady=5, sticky='w')# 設置 Entry 位置

# 建立影像格式下拉式選單
format_var = tk.StringVar()
format_choices = ["jpg", "png"]
format_dropdown = ttk.Combobox(window, values=format_choices, textvariable=format_var, state="readonly", width=4)
format_dropdown.set(format_choices[0])
format_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky='w')

# 建立儲存位置選單
def on_enter_key(event):
    start_download()
# 為整個窗口綁定 Enter 鍵與 on_enter_key 函數
window.bind('<Return>', on_enter_key)
# 建立下載按鈕並綁定事件
button_start = ttk.Button(window, text="下載", command=start_download, style='A.TButton')# 建立下載按鈕
button_start.grid(row=2, column=0, padx=10, pady=5, rowspan=2, sticky='w')

# 添加更換背景圖片的按鈕，並永遠保持在Tkinter的最左下角
def choose_background_image():
    response = messagebox.askokcancel("建議","建議選擇尺寸16 : 9的背景圖片")
    # 讓使用者選擇背景圖片文件
    if response:
        # 讓使用者選擇背景圖片文件
        file_path = filedialog.askopenfilename()
        if file_path:
            # 調用裁剪並設置背景圖片的函數
            crop_and_set_background(file_path)
button_change_bg = ttk.Button(window, text="更換背景", style='B.TButton', command=choose_background_image)# 建立更換背景圖片按鈕
button_change_bg.place(relx=0.0, rely=1.0, anchor='sw')

# 定義顯示作者的函數
def show_author():
    messagebox.showinfo("關於", "作者 : 趙子文\n版本:  ver.9\n使用自動化瀏覽器模擬操作\n方便大量下載圖片")

# 建立關於按鈕
btn_about = ttk.Button(window, text="關於", style='A.TButton', command=show_author)
btn_about.place(relx=1.0, rely=1.0, anchor='se')

# 讓視窗運行起來，進入主迴圈，等待視窗上的事件發生並執行對應的回應
window.mainloop()