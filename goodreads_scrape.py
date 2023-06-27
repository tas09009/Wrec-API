"""
Export User's books
"""

from urllib.parse import urlencode
import requests

# from bs4 import BeautifulSoup
import re
from lxml import html
import csv
import time
from io import StringIO
from flask import abort

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from urllib.request import urlopen
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import xmltodict

from models import Book, User
from db import db

login_buttons = {
    "amazon": 1
}

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

def get_login_links():
    """
    User selected their login type (Amazon, Facebook, etc.)
    """
    #TODO: Add proxies since you can't pass headers into selenium:
    # https://stackoverflow.com/questions/15645093/setting-request-headers-in-selenium
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--disable-dev-shm-usage")

    browser = webdriver.Firefox(options=firefox_options)
    browser.get("https://www.goodreads.com/user/sign_in")
    buttons = browser.find_elements(By.TAG_NAME, "button")
    return buttons, browser

# user_data = {"email": "taniya.singh12@gmail.com", "password": "tansin"}
def sign_in(login_links, browser, user_data):
    # Sign into Amazon
    amazon_signin_button = login_links[login_buttons["amazon"]]
    amazon_signin_button.click()
    original_window = browser.window_handles[0]
    time.sleep(3)
    browser.switch_to.window(browser.window_handles[0])
    email_input = browser.find_element(By.XPATH, '//input[@id="ap_email"]') #TODO: email/phone number. If not in database, add
    password_input = browser.find_element(By.XPATH, '//input[@id="ap_password"]')
    time.sleep(2)
    email_input.send_keys(user_data["email"])
    user = User.query.filter_by(email=user_data["email"]).first()
    # time.sleep(4)
    password_input.send_keys(user_data["password"])
    time.sleep(3)
    submit_button = browser.find_element(By.XPATH, '//input[@id="signInSubmit"]')
    submit_button.send_keys(Keys.ENTER)
    browser.switch_to.window(original_window)

    # Good Reads: get user_id & cookies
    time.sleep(7)
    tree = html.fromstring(browser.page_source)
    my_books = tree.xpath('//a[contains(text(), "My Books")]')[0].get("href")
    user_id = "".join(re.findall("\d", my_books))
    return user_id, user


def transfer_session(browser):
# Transfer selenium.webdriver to requests.session
    session = requests.Session()
    session.headers.update(headers)
    for cookie in browser.get_cookies():
        cookie = {cookie["name"]: cookie["value"]}
        session.cookies.update(cookie)
    return session


def export_book(session, user_id, user):
    exported_books_csv = session.get(
        EXPORT_CSV_BASE_URL + user_id + "/goodreads_export.csv",
    )

    # Generate a csv
    if not exported_books_csv:
        seconds_waited = 0
        while not exported_books_csv and seconds_waited <= 15:
            data = {'format': 'json'}
            export_url = EXPORT_CSV_BASE_URL + user_id
            session.get(export_url, headers=headers, data=data) # export books button
            time.sleep(5)
            seconds_waited += 5
            exported_books_csv = session.get(
                EXPORT_CSV_BASE_URL + user_id + "/goodreads_export.csv",
            )
        print({"Message": "Error: Could not export user's books"}) # return statement
    dataFile = StringIO(exported_books_csv.text)
    csv_reader = csv.reader(dataFile)

    #TODO: change to name instead of user_id
    #TODO: What about books with no isbn values?
    # [ ] Each row should just get added directly to database instead of adding to a csv file
    # [ ] make webdriver headless
    with open(f"csv_files/{user_id}_csv_export.csv", "w", newline="") as csv_file:
        # writer = csv.writer(csv_file)
        next(csv_reader) # skip headers
        for line in csv_reader:
            ISBN_IDX = 5
            TITLE_IDX = 1
            AUTHOR_IDX = 2
            isbn_value = line[ISBN_IDX]
            title = line[TITLE_IDX]
            author = line[AUTHOR_IDX]
            book = Book.query.filter_by(isbn=isbn_value).first()

            # [x] Else: add book to user. Skip this row in csv entirely
            # if book_with_isbn:
                # book = Book.query.filter_by(isbn=isbn).first_or_404()
            # [x] If: book doesn't exist, add it to Books
            if not book:
                dewey_decimal = get_dewey_value(isbn=isbn_value, title=title, author=author)
                book = Book(isbn=isbn_value, title=title, author=author, dewey_decimal=dewey_decimal)
                # line["dewey_decimal"] = dewey_decimal
                # writer.writerow(line.values())

            user.books.append(book)
            db.session.add(user)
            db.session.commit()




def get_dewey_value(isbn, title, author):
    """
    Use Classify API to find the dewey decimal number using:
    1. ISBN: uses isbn_to_dewey()
    OR
    2. title & author

    returns XML data for each book. Parse until dewey decimal
    number is found
    """

    base = "http://classify.oclc.org/classify2/Classify?"
    summaryBase = "&summary=true"

    if isbn:
        parm_type = "isbn"
        parm_value = str(isbn)
        search_url = (
            base + urlencode({parm_type: parm_value.encode("utf-8")}) + summaryBase
        )

    else:
        param_type_title = "title"
        parm_value_title = title
        param_type_author = "author"
        parm_value_author = author
        search_url = (
            base
            + urlencode({param_type_title: parm_value_title.encode("utf-8")})
            + "&"
            + urlencode({param_type_author: parm_value_author.encode("utf-8")})
            + summaryBase
        )

    # xml_content = urlopen(search_url).read()
    xml_content = requests.get(search_url).text
    book_data = xmltodict.parse(xml_content)
    return isbn_to_dewey(book_data)


def isbn_to_dewey(book_data):
    """
    Traverse though dictionary to find the dewey value.
    response_code determines how to traverse
    """
    response_code = book_data.get("classify").get("response").get("@code")
    SINGLE_BOOK = "0"
    MULTIPLE_BOOKS = "4"

    if response_code == SINGLE_BOOK:
        try:
            dewey_number = (
                book_data.get("classify")
                .get("recommendations")
                .get("ddc")
                .get("mostPopular")
                .get("@sfa")
            )
            return dewey_number
        except AttributeError:
            return "Returned book response, but has no dewey number"

    elif response_code == MULTIPLE_BOOKS:
        try:
            owi_number = (
                book_data.get("classify").get("works").get("work")[0].get("@owi")
            )

            base = "http://classify.oclc.org/classify2/Classify?"
            parm_type = "owi"
            parm_value = owi_number
            search_url = base + urlencode({parm_type: parm_value.encode("utf-8")})
            xml_content = urlopen(search_url).read()
            book_data = xmltodict.parse(xml_content)

            dewey_number = (
                book_data.get("classify")
                .get("recommendations")
                .get("ddc")
                .get("mostPopular")
                .get("@sfa")
            )
            return dewey_number
        except AttributeError:
            return "multiple works found, even after using OWI"
    else:
        return "Cannot find dewey"


# --------------- NOT USING ANYMORE ---------
# login_links, browser = get_login_links()
# user_id = sign_in(login_links, browser, user_data)
# session = transfer_session(browser)
# export_book(session, user_id)

# homepage_response = session.get('https://www.goodreads.com')
# session.get('https://www.goodreads.com/review/import')
