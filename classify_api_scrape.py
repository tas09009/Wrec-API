import requests

from urllib.parse import urlencode
from urllib.request import urlopen
import xmltodict

from lxml import etree

def get_dewey_value_scrape(isbn=None, title=None, author=None):
    base_url = 'http://classify.oclc.org'
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