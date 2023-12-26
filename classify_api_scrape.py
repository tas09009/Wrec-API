from urllib.parse import urlencode, urlunparse

import time
import requests
import unicodedata
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from urllib.parse import urlencode
from urllib.request import urlopen
import xmltodict

from lxml import etree


logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logfile_unimported_books.log')
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_dewey_value_scrape_selenium(isbn=None, title=None, author=None) -> int:
    driver = create_driver()

    base_url = 'classify.oclc.org'
    path = '/classify2/ClassifyDemo'
    DEWEY_VALUE_XPATH = '//table[@id="classSummaryData"]/tbody/tr/td[2]'
    result_url = None

    # Prepare the query parameters based on the provided input
    params = {}
    params['startRec'] = 0
    if isbn:
        params['search-standnum-txt'] = isbn
    elif title and author:
        params['search-title-txt'] = title
        params['search-author-txt'] = author

    query_string = urlencode(params)
    full_url = urlunparse(('https', base_url + path, '', '', query_string, ''))
    driver.get(full_url)
    time.sleep(5)
    try:
        if result_link := driver.find_element(By.XPATH, '//span[@class="title"]/a'):
            result_link.click()
        ddc_class_number = driver.find_element(By.XPATH, DEWEY_VALUE_XPATH).text
        try:
            return int(float(ddc_class_number))
        except ValueError:
            pass
    except NoSuchElementException:
        logger.info(
            'Selenium unable to search for book, isbn="%s", title="%s", author="%s"',
            isbn, title, author
        )
        return 0 # placeholder value

def create_driver():
    """
    Create driver to webscrape dewey values
    Response using requests library: Enable JavaScript and cookies to continue"
    """
    #TODO: Add rotating user agents
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134"


    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage') # Overcomes limited resource problems
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Disables the flag that identifies WebDriver sessions
    chrome_options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    return driver


def get_dewey_value_scrape(isbn=None, title=None, author=None):

    base_url = 'https://classify.oclc.org'
    path = '/classify2/ClassifyDemo'
    DEWEY_VALUE_XPATH = '//table[@id="classSummaryData"]/tbody/tr/td[2]/text()'
    result_url = None

    # Prepare the query parameters based on the provided input
    params = {}
    params['startRec'] = 0
    if isbn:
        params['search-standnum-txt'] = isbn
    elif title and author:
        params['search-title-txt'] = title
        params['search-author-txt'] = author

    response = requests.get(base_url + path, params=params)
    if "Sorry, your current search did not return any results" in response.text:
        return None
    tree = etree.HTML(response.content)

    if isbn:
        ddc_class_number = tree.xpath(DEWEY_VALUE_XPATH)[0]
        try:
            return int(float(ddc_class_number))
        except ValueError:
            pass

    # title and author
    result_link = tree.xpath('//span[@class="title"]/a')
    if result_link:
        result_url = result_link[0].get('href')

    if result_url:
        response = requests.get(base_url + result_url)
        tree = etree.HTML(response.content)
        ddc_class_number = tree.xpath(DEWEY_VALUE_XPATH)[0]
        try:
            return int(float(ddc_class_number))
        except ValueError:
            pass

    return None

# ------------ API IS NO LONGER PUBLICLY ACCSESSIBLE --------
def get_dewey_value_api(isbn, title, author):
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