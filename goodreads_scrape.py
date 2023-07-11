"""
Export User's books
"""

import os
import re
import logging
from lxml import html
import csv
import time
from io import StringIO
from flask import abort
import requests

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from models import Book
from db import db
from classify_api_scrape import get_dewey_value_scrape

log_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s %(extra)s')
logging.basicConfig(filename="logfile_unimported_books.log", level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger('my_logger')

for handler in logger.handlers:
    handler.setFormatter(log_formatter)


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

headers_export = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "DNT": "1",
    "Origin": "https://www.goodreads.com",
    "Referer": "https://www.goodreads.com/review/import",
    "Related-Request-Id": "E79SFFS8EHVME3R7H9T6",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "X-CSRF-Token": "uOBkixfdYNmELVyukKOACqLk3aFG7Dow+xbYQYvx4vhHc42tlHhXZi3lTHtca/PMCGXYuVHKiGsXUL3fZPi3nQ==",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
}


def get_login_links():
    """
    User selected their login type (Amazon, Facebook, etc.)
    """
    # TODO: Add proxies since you can't pass headers into selenium:
    # https://stackoverflow.com/questions/15645093/setting-request-headers-in-selenium

    BROWSERLESS_API_KEY = os.getenv("BROWSERLESS_API_TOKEN")
    ENVIRONMENT_KEY = os.getenv("FLASK_DEBUG")
    # Production
    if not ENVIRONMENT_KEY:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.set_capability('browserless:token', BROWSERLESS_API_KEY)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")

        browser = webdriver.Remote(
            command_executor='https://chrome.browserless.io/webdriver',
            options=chrome_options
        )

    # Development
    elif ENVIRONMENT_KEY == 1:
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--disable-dev-shm-usage")
        browser = webdriver.Firefox(options=firefox_options)

    browser.get("https://www.goodreads.com/user/sign_in")
    login_buttons = browser.find_elements(By.XPATH, "//button")
    return login_buttons, browser


def facebook_sign_in(login_buttons, button_idx, browser, user_data):
    time.sleep(3)
    sign_in_button = login_buttons[button_idx]
    sign_in_button.click()
    time.sleep(3)
    email_input = browser.find_element(
        By.XPATH, '//input[@id="email"]'
    )  # TODO: email/phone number. If not in database, add
    password_input = browser.find_element(By.XPATH, '//*[@id="pass"]')
    time.sleep(2)
    email_input.send_keys(user_data["email"])
    password_input.send_keys(user_data["password"])
    time.sleep(3)
    submit_button = browser.find_element(By.XPATH, '//button[@id="loginbutton"]')
    submit_button.send_keys(Keys.ENTER)
    return get_user_id(browser)


def amazon_sign_in(login_buttons, button_idx, browser, user_data):
    time.sleep(3)
    amazon_signin_button = login_buttons[button_idx]
    amazon_signin_button.click()
    time.sleep(3)
    email_input = browser.find_element(
        By.XPATH, '//input[@id="ap_email"]'
    )  # TODO: email/phone number. If not in database, add
    password_input = browser.find_element(By.XPATH, '//input[@id="ap_password"]')
    time.sleep(2)
    email_input.send_keys(user_data["email"])
    password_input.send_keys(user_data["password"])
    time.sleep(3)
    submit_button = browser.find_element(By.XPATH, '//input[@id="signInSubmit"]')
    submit_button.send_keys(Keys.ENTER)
    return get_user_id(browser)


def google_sign_in(login_buttons, button_idx, browser, user_data):
    time.sleep(3)
    sign_in_button = login_buttons[button_idx]
    sign_in_button.click()
    time.sleep(3)
    email_input = browser.find_element(
        By.XPATH, '//input[@aria-label="Email or phone"]'
    )  # TODO: email/phone number. If not in database, add
    time.sleep(2)
    email_input.send_keys(user_data["email"])
    next_button = browser.find_element(By.XPATH, '//button[@jsname="LgbsSe"]')
    next_button.click()

    password_input = browser.find_element(By.XPATH, '//input[@id="ap_password"]')
    password_input.send_keys(user_data["password"])
    time.sleep(3)
    submit_button = browser.find_element(By.XPATH, '//input[@id="signInSubmit"]')
    submit_button.send_keys(Keys.ENTER)
    return get_user_id(browser)


def apple_sign_in(login_buttons, button_idx, browser, user_data):
    time.sleep(3)
    sign_in_button = login_buttons[button_idx]
    sign_in_button.click()
    time.sleep(3)
    email_input = browser.find_element(
        By.XPATH, '//input[@id="account_name_text_field"]'
    )  # TODO: email/phone number. If not in database, add
    time.sleep(2)
    email_input.send_keys(user_data["email"])
    next_button = browser.find_element(By.XPATH, '//button[@aria-label="Continue"]')
    next_button.click()

    password_input = browser.find_element(
        By.XPATH, '//input[@id="password_text_field"]'
    )
    password_input.send_keys(user_data["password"])
    time.sleep(3)
    submit_button = browser.find_element(By.XPATH, '//button[@id="sign-in"]')
    submit_button.send_keys(Keys.ENTER)
    return get_user_id(browser)


def goodreads_sign_in(login_buttons, button_idx, browser, user_data):
    time.sleep(3)
    sign_in_button = login_buttons[button_idx]
    sign_in_button.click()
    time.sleep(3)
    email_input = browser.find_element(
        By.XPATH, '//input[@id="ap_email"]'
    )  # TODO: email/phone number. If not in database, add
    password_input = browser.find_element(By.XPATH, '//input[@id="ap_password"]')
    time.sleep(2)
    email_input.send_keys(user_data["email"])
    password_input.send_keys(user_data["password"])
    time.sleep(3)
    submit_button = browser.find_element(By.XPATH, '//input[@id="signInSubmit"]')
    submit_button.send_keys(Keys.ENTER)
    return get_user_id(browser)


def get_user_id(browser):
    time.sleep(7)
    check_for_popups(browser)
    tree = html.fromstring(browser.page_source)
    time.sleep(1)
    my_books = tree.xpath('//a[contains(text(), "My Books")]')[0].get("href")
    user_id = "".join(re.findall("\d", my_books))
    return user_id, browser


def check_for_popups(browser):
    try:
        if browser.find_element(
            By.XPATH, '//*[contains(text(), "been a while since you logged into")]'
        ):
            browser.find_element(By.XPATH, '//span[text()="Continue"]').click()
        if browser.find_element(By.XPATH, '//div[@class="right"]/h1/text()'):
            abort(500, message="Goodreads is down for maintenance.")
        if browser.find_element(
            By.XPATH,
            '//*[contains(text(), "This Apple ID has been locked for security reasons")]',
        ):
            abort(500, message="This Apple ID has been locked for security reasons")
        if browser.find_element(
            By.XPATH,
            '//*[contains(text(), "To better protect your account, please re-enter your")]',
        ):
            abort(
                500,
                message="Your password needs verification on goodread's website. Please log into Goodreads first on another browser.",
            )
    except NoSuchElementException:
        pass


def transfer_session(browser):
    # Transfer selenium.webdriver to requests.session
    session = requests.Session()
    session.headers.update(headers)
    for cookie in browser.get_cookies():
        cookie = {cookie["name"]: cookie["value"]}
        session.cookies.update(cookie)
    browser.quit()
    return session


def export_book(session, user_id, user):
    exported_books_csv = session.get(EXPORT_CSV_BASE_URL + user_id)

    # Generate a csv
    if not exported_books_csv:
        seconds_waited = 0
        while not exported_books_csv and seconds_waited <= 15:
            data = {"format": "json"}
            export_url = EXPORT_CSV_BASE_URL + user_id
            session.get(
                export_url, headers=headers_export, data=data
            )  # export books button
            time.sleep(5)
            seconds_waited += 5
            exported_books_csv = session.get(
                EXPORT_CSV_BASE_URL + user_id + "/goodreads_export.csv",
            )
        if not exported_books_csv:
            abort(500, "Error: Could not export user's books")  # return statement

    dataFile = StringIO(exported_books_csv.text)
    csv_reader = csv.reader(dataFile)
    headers_csv = next(csv_reader)  # skip headers
    ISBN_IDX = 5
    TITLE_IDX = 1
    AUTHOR_IDX = 2
    for line in csv_reader:
        isbn_value = line[ISBN_IDX] if line[ISBN_IDX].isdigit() else None
        title = line[TITLE_IDX]
        author = line[AUTHOR_IDX]
        book = Book.query.filter_by(title=title).first()
        if book:
            user.books.append(book)
        else:
            dewey_decimal = get_dewey_value_scrape(
                isbn=isbn_value, title=title, author=author
            )
            if dewey_decimal:
                book = Book(
                    isbn=isbn_value,
                    title=title,
                    author=author,
                    dewey_decimal=dewey_decimal,
                )
                db.session.add(book)
                user.books.append(book)
            else:
                # [ ] log books that don't have value - with book info
                logger.info(
                    "Book without dewey number",
                    extra={"isbn": isbn_value, "title": title, "author": author},
                )
    db.session.commit()

    return {
        "message": f"Successfully downloaded all books into a csv_file for user_id: {user_id}",
        "redirect link": f"/bookshelf/user/<int:user_id>",
    }
