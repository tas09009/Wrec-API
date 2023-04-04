"""
Export User's books
"""

import requests

# from bs4 import BeautifulSoup
import re
from lxml import html
import csv
import time
from io import StringIO

# homepage_response = session.get('https://www.goodreads.com')
# session.get('https://www.goodreads.com/review/import')

from selenium import webdriver
from urllib.request import urlopen
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

EXPORT_CSV_BASE_URL = "https://www.goodreads.com/review_porter/export/"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Referer": "https://www.goodreads.com/review/import",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}

# Add proxies since you can't pass headers into selenium:
# https://stackoverflow.com/questions/15645093/setting-request-headers-in-selenium
browser = webdriver.Firefox()
browser.get("https://www.goodreads.com/user/sign_in")
buttons = browser.find_elements(By.TAG_NAME, "button")
amazon_signin_button = buttons[1]
amazon_signin_button.click()

# Sign into Amazon
original_window = browser.window_handles[0]
time.sleep(2)
browser.switch_to.window(browser.window_handles[1])
email_input = browser.find_element(By.XPATH, '//input[@id="ap_email"]')
password_input = browser.find_element(By.XPATH, '//input[@id="ap_password"]')
time.sleep(2)
email_input.send_keys("taniya.singh12@gmail.com")
time.sleep(4)
password_input.send_keys("tansin")
time.sleep(3)
submit_button = browser.find_element(By.XPATH, '//input[@id="signInSubmit"]')
submit_button.send_keys(Keys.ENTER)
browser.switch_to.window(original_window)

# Good Reads: get user_id & cookies
time.sleep(7)
tree = html.fromstring(browser.page_source)
my_books = tree.xpath('//a[contains(text(), "My Books")]')[0].get("href")
user_id = "".join(re.findall("\d", my_books))
session = requests.Session()
session.headers.update(headers)
selenium_cookies = browser.get_cookies()
cookie_dict = {cookie["name"]: cookie["value"] for cookie in selenium_cookies}


# TODO: generate a new csv file to download - currently NOT working
# Response -> Book Model
session.get(
    EXPORT_CSV_BASE_URL + user_id,
    cookies=cookie_dict,
)
exported_books_csv = session.get(
    EXPORT_CSV_BASE_URL + user_id + "/goodreads_export.csv",
)
dataFile = StringIO(exported_books_csv.text)
csv_reader = csv.reader(dataFile)

# for row in csv_reader:
    # print(row, "\n\n")