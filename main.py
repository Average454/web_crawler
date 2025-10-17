from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import docx
import time

def clean_chapter(text: str) -> str:
    start_key = "《我的女友來自未來！》"##《 》改成你所抓的書名
    end_key = "(本章完)"
    start_idx = text.find(start_key)
    if start_idx != -1:
        text = text[start_idx + len(start_key):]
    end_idx = text.find(end_key)
    if end_idx != -1:
        text = text[:end_idx]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

file = docx.Document()
book_index_url = "https://czbooks.net/n/s6lnhk" ##自行輸入小說的網址

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 改成 False 可看瀏覽器畫面
    page = browser.new_page()

    print("📖 正在載入目錄頁...")
    page.goto(book_index_url, timeout=60000)
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    chapter_list = soup.find("ul", class_="nav chapter-list", id="chapter-list")
    if not chapter_list:
        print("找不到章節列表 (id=chapter-list)")
    else:
        chapters = chapter_list.find_all("a")
        print(f"共找到 {len(chapters)} 個章節")

    for idx, ch in enumerate(chapters[50:100], 1):  # 自行調整要從哪章開始抓
        title = ch.get_text(strip=True)
        link = ch.get("href")

        # 修正相對路徑
        if link.startswith("//"):
            link = "https:" + link
        elif link.startswith("/"):
            link = "https://czbooks.net" + link

        print(f"[{idx}] 正在抓取：{title}")

        page.goto(link, timeout=60000)
        time.sleep(2)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        content_div = soup.find("div", class_="content")
        if content_div:                                              
            text = clean_chapter(content_div.get_text())
            for line in text.splitlines():
                file.add_paragraph(line)
        file.save("我的女友來自未來！.docx")##自行改成要存檔的名稱
    else:
        print(f"⚠️ 找不到內容：{title}")
        file.save("我的女友來自未來！.docx")##自行改成要存檔的名稱
        print("📘 全部章節儲存完成")

    browser.close()

