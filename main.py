import json
import os
from config import path
from tabnanny import check
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

ALL_NEWS_URL = "https://www.binance.com/ru/support/announcement/c-48?navId=48"
SITE_URL = "https://www.binance.com"

ALL_NEWS_CLASS = "css-1ey6mep"
NEWS_TITLE_CLASS = "css-f94ykk"

DRIVER_PATH = path

DATE_DIGITS_TO_DELETE = -10

def get_html():

    options = Options()
    options.headless = True
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(service = Service(DRIVER_PATH), options = options)
    url = ALL_NEWS_URL

    driver.get(url)

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    driver.close()

    return soup

def find_all_news():
    return get_html().find_all('a', class_ = ALL_NEWS_CLASS)

def get_news_date(current_news):
    format_date = current_news.find("div", class_ = NEWS_TITLE_CLASS).text.strip()[DATE_DIGITS_TO_DELETE:]
    format_date = format_date.replace('-', '.')
    return format_date[-2:] + format_date[-6:][:-2] + format_date[:-6]

def get_news_title(current_news):
    return current_news.find("div", class_ = NEWS_TITLE_CLASS).text.strip()[:DATE_DIGITS_TO_DELETE]

def get_news_url(current_news):
    return f'{SITE_URL}{current_news.get("href")}'

def get_news_id(current_news_url):
    return current_news_url.split("/")[-1]

def add_news_in_list(all_news_list, news_date, news_title, news_url, news_id):
    all_news_list[news_id] = {
            "news_date": news_date,
            "news_title": news_title,
            "news_url": news_url
        }

def save_news_json(all_news_list):
    with open(os.path.join("binance-news-bot-ru-py","news.json"), "w", encoding = "utf-8") as file:
        json.dump(all_news_list, file, indent = 4, ensure_ascii = False)

def load_news_json():
    with open(os.path.join("binance-news-bot-ru-py", "news.json"), encoding = "utf-8") as file:
        return json.load(file)



def get_first_news():
    all_news_list = {}
    all_news = find_all_news()

    for current_news in all_news:
        news_date = get_news_date(current_news)
        news_title = get_news_title(current_news)
        news_url = get_news_url(current_news)
        news_id = get_news_id(news_url)
        add_news_in_list(all_news_list, news_date, news_title, news_url, news_id)

    save_news_json(all_news_list)

def check_news_update():
    news_list_json = load_news_json()

    all_news = find_all_news()
    latest_news = {}

    for current_news in all_news:
        news_date = get_news_date(current_news)
        news_url = get_news_url(current_news)
        news_id = get_news_id(news_url)

        if news_id not in news_list_json:
            news_title = get_news_title(current_news)
            add_news_in_list(news_list_json, news_date, news_title, news_url, news_id)
            add_news_in_list(latest_news, news_date, news_title, news_url, news_id)

    save_news_json(news_list_json)
    return latest_news


def main():
    get_first_news()
    # check_news_update()

if __name__ == '__main__':
    main()