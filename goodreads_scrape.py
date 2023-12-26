"""
Helper methods for resources/auth.py
"""

import os
import re
import logging
from lxml import html
import csv
import time
import unicodedata
from io import StringIO
from flask import abort
import chardet
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models import Book, User
from db import db
from classify_api_scrape import get_dewey_value_scrape_selenium

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logfile_unimported_books.log')
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


# logger setup for unimported books
logger_books = logging.getLogger('books_logger')
logger_books.setLevel(logging.INFO)
handler_books = logging.FileHandler('logfile_unimported_books.log')
formatter_books = logging.Formatter(
    '[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler_books.setFormatter(formatter_books)
logger_books.addHandler(handler_books)

# logger setup for unscrapable elements during web scraping
logger_scraping = logging.getLogger('scraping_logger')
logger_scraping.setLevel(logging.INFO)
handler_scraping = logging.FileHandler('logfile_unscrapable_elements.log')
formatter_scraping = logging.Formatter(
    '[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler_scraping.setFormatter(formatter_scraping)
logger_scraping.addHandler(handler_scraping)


START_EXPORT_CSV_BASE_URL = "https://www.goodreads.com/review_porter/export/{gr_user_id}/goodreads_export.csv"
EXPORTED_CSV_BASE_URL = "https://www.goodreads.com/review_porter/export/{gr_user_id}/goodreads_export.csv"

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
    # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134"
    user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"

    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage') # Overcomes limited resource problems
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Disables the flag that identifies WebDriver sessions
    chrome_options.add_argument(f"user-agent={user_agent}")
    browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    browser.get("https://www.goodreads.com/user/sign_in")
    try:
        login_buttons = browser.find_elements(By.XPATH, "//a")
    except Exception as e:
        logger_scraping.error('Element XPath has probably changed', exc_info=True)

    return login_buttons, browser


def facebook_sign_in(login_buttons, button_idx, browser, user_data):
    time.sleep(3)
    sign_in_button = login_buttons[button_idx]
    sign_in_button.click()
    time.sleep(3)
    email_input = browser.find_element(
        By.XPATH, '//input[@id="email"]'
    )
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
    time.sleep(2)
    email_input = browser.find_element(
        By.XPATH, '//input[@id="ap_email"]'
    )
    password_input = browser.find_element(By.XPATH, '//input[@id="ap_password"]')
    time.sleep(3)
    email_input.send_keys(user_data["email"])
    password_input.send_keys(user_data["password"])
    time.sleep(4)
    submit_button = browser.find_element(By.XPATH, '//input[@id="signInSubmit"]')
    time.sleep(2)
    submit_button.send_keys(Keys.ENTER)
    return get_user_id(browser)


def google_sign_in(login_buttons, button_idx, browser, user_data):
    time.sleep(3)
    sign_in_button = login_buttons[button_idx]
    sign_in_button.click()
    time.sleep(3)
    email_input = browser.find_element(
        By.XPATH, '//input[@aria-label="Email or phone"]'
    )
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
    )
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
    )
    password_input = browser.find_element(By.XPATH, '//input[@id="ap_password"]')
    time.sleep(2)
    email_input.send_keys(user_data["email"])
    password_input.send_keys(user_data["password"])
    time.sleep(3)
    submit_button = browser.find_element(By.XPATH, '//input[@id="signInSubmit"]')
    submit_button.send_keys(Keys.ENTER)
    return get_user_id(browser)


def get_user_id(browser):
    check_for_popups(browser)
    # time.sleep(2)
    tree = html.fromstring(browser.page_source)
    try:
        my_books = tree.xpath('//a[contains(text(), "My Books")]')[0].get("href")
        user_id = "".join(re.findall("\d", my_books))
    except Exception as e:
        solve_puzzle_text = tree.xpath('//*[contains(text(), "Solve this puzzle")]')
        if solve_puzzle_text:
            logger_scraping.error('Element XPath has probably changed', exc_info=True)
            return

    return user_id, browser


def check_for_popups(browser):
    try:
        # Another one to add: Goodreads is taking too long
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
    """Transfer selenium.webdriver to requests.session"""
    session = requests.Session()
    session.headers.update(headers)
    for cookie in browser.get_cookies():
        cookie = {cookie["name"]: cookie["value"]}
        session.cookies.update(cookie)
    browser.quit()
    return session


#TODO: better way to pass the user object around?
def export_book(session, gr_user_id, user):
    START_EXPORT_CSV_BASE_URL = "https://www.goodreads.com/review_porter/export/{gr_user_id}"
    EXPORTED_CSV_BASE_URL = "https://www.goodreads.com/review_porter/export/{gr_user_id}/goodreads_export.csv"

    start_export_csv = session.post(START_EXPORT_CSV_BASE_URL.format(gr_user_id=gr_user_id))
    time.sleep(5)
    exported_books_csv = session.get(EXPORTED_CSV_BASE_URL.format(gr_user_id=gr_user_id))

    # See if this was enough time to export
    if exported_books_csv.status_code != requests.codes.ok: #TODO: not working
        seconds_waited = 0
        while not exported_books_csv and seconds_waited <= 15:
            data = {"format": "json"}
            export_url = EXPORTED_CSV_BASE_URL.format(gr_user_id=gr_user_id)
            session.post(
                export_url, headers=headers_export, data=data
            )  # export books button
            time.sleep(5)
            seconds_waited += 5
            exported_books_csv = session.get(EXPORTED_CSV_BASE_URL.format(gr_user_id=gr_user_id))
        exported_books_csv.raise_for_status()


    # Check for the encoding of the CSV content
    result = chardet.detect(exported_books_csv.content) # exported_books_csv: Response() object
    charset = result['encoding']

    # Use the detected encoding to decode the content
    dataFile = StringIO(exported_books_csv.content.decode(charset))
    csv_reader = csv.reader(dataFile)
    headers_csv = next(csv_reader)  # skip headers

    ISBN_IDX = 5
    TITLE_IDX = 1
    AUTHOR_IDX = 2

    # Test with the first 5 books
    counter = 1
    for line in csv_reader:
        if counter == 5:
            break
        isbn_value = line[ISBN_IDX] if line[ISBN_IDX].isdigit() else None
        title_raw = line[TITLE_IDX]
        author_raw = line[AUTHOR_IDX]

        # Normalize the author name and title
        author = unicodedata.normalize('NFD', author_raw).encode('ascii', 'ignore').decode('utf-8')
        title = unicodedata.normalize('NFD', title_raw).encode('ascii', 'ignore').decode('utf-8')
        book = Book.query.filter_by(title=title).first()
        if book:
            user.books.append(book)
        else:
            dewey_decimal = get_dewey_value_scrape_selenium(
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
                logger.info(
                    'Book added, isbn="%s", title="%s", author="%s"',
                    isbn_value, title, author
                )
            else:
                # [ ] log books that don't have value - with book info
                logger.info(
                    'Book without dewey number, isbn="%s", title="%s", author="%s"',
                    isbn_value, title, author
                )

        counter += 1
    try:
        db.session.commit()
    except IntegrityError:
        abort(400, message=f"Unable to add books for {user.email}")
    except SQLAlchemyError as e:
        abort(500, message=str(e))
