from urllib.request import urlopen
from urllib.parse import urlencode
# import re

from flask import request, redirect, url_for, jsonify
from flask_login import login_required, current_user
# import flask_excel as excel  # not being used?
import xmltodict

from app.models import (
    Book,
    # User,
    TenCategories,
    HundredCategories,
    ThousandCategories,
)
from . import api
from .. import db


# http://127.0.0.1:5000/api/v1/books/upload
@api.route("/books/upload", methods=["GET", "POST"])
@login_required
def csv_import():
    """Upload a goodreads csv file > populate database."""

    if request.method == "POST":
        resp = jsonify({"result": request.get_array(field_name='file')})
        result = resp.get_json()

        books_upload = result["result"]

        TITLE = 1
        AUTHOR = 2
        ISBN = 5
        ISBN13 = 6
        for book_item in books_upload:
            title = book_item[TITLE]
            author = book_item[AUTHOR]
            isbn = book_item[ISBN]
            isbn13 = book_item[ISBN13]
            print('book attributes: ', title, author, isbn, isbn13, '\n')
            determine_book_unique(isbn, isbn13, title, author)

        populate_nested_structure()
        return redirect(url_for("main.view_books_by_user"))

    return """
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    """

def determine_book_unique(isbn, isbn13, title, author):
    """
    if: book doesn't exist in the database, add it,
    else: find book in database, add the current_user to the book's list
    """
    book_isbn = Book.query.filter_by(isbn=str(isbn)).first()
    book_isbn13 = Book.query.filter_by(isbn13=str(isbn13)).first()
    book_title = Book.query.filter_by(title=title).first()
    book_author = Book.query.filter_by(author=author).first()
    if book_isbn is None or book_isbn13 is None or (book_title and book_author is None):
        book_instance = Book(title=title, author=author, isbn=isbn, isbn13=isbn13)
        book_instance.classify_ddc = request_dewey(book_instance)
        book_instance.classify_ten_id = dewey_to_category_ten(book_instance.classify_ddc)
        book_instance.classify_hundred_id = dewey_to_category_hundred(book_instance.classify_ddc)
        book_instance.classify_thousand_id = dewey_to_category_thousand(book_instance.classify_ddc)
        current_user.books.append(book_instance)
        db.session.add(book_instance)
        db.session.add(current_user)
        db.session.commit()
        print("Unique book, adding: ", book_instance, '\n')
    else:
        book_in_database = Book.query.filter_by(isbn=str(isbn)).first() or \
            Book.query.filter_by(isbn13=str(isbn13)).first() or \
            Book.query.filter_by(title=title, author=author).first()
        book_in_database.users.append(current_user)
        db.session.add(book_in_database)
        db.session.commit()
        print("Book exists, skipping: ", book_in_database, '\n')


@api.route("/dewey/", methods=["GET"])
def request_dewey(book_instance):
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

    if book_instance.isbn:
        parm_type = "isbn"
        parm_value = str(book_instance.isbn)
        search_url = (
            base
            + urlencode({parm_type: parm_value.encode("utf-8")})
            + summaryBase
        )
    
    elif not book_instance.isbn:
        parm_type_title = "title"
        parm_value_title = book_instance.title
        parm_type_author = "author"
        parm_value_author = book_instance.author
        search_url = (
            base
            + urlencode({parm_type_title: parm_value_title.encode("utf-8")})
            + "&"
            + urlencode({parm_type_author: parm_value_author.encode("utf-8")})
            + summaryBase
        )

    xml_content = urlopen(search_url).read()
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
            owi_number = book_data.get("classify").get("works").get("work")[0].get("@owi")

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
    else: return 'Cannot find dewey'


def dewey_to_category_ten(dewey_number):
    ten_cat = TenCategories.query.all()

    firstNum_ten = dewey_number[0]
    for category in ten_cat:
        if firstNum_ten == category.call_number[0]:
            return category.id


def dewey_to_category_hundred(dewey_number):
    hun_cat = HundredCategories.query.all()

    firstNum_hundred = dewey_number[0:2]
    for category in hun_cat:
        if firstNum_hundred == category.call_number[0:2]:
            return category.id


def dewey_to_category_thousand(dewey_number):
    thou_cat = ThousandCategories.query.all()

    firstNum_thousand = dewey_number[0:3]
    for category in thou_cat:
        if firstNum_thousand == category.call_number[0:3]:
            return category.id


def populate_nested_structure():
    """
    nest 100 'HundredCategories' within 10 'TenCategories'
    nest 100 'ThousandCategories' within 10 'HundredCategories'
    """
    def populate_ten_classes():
        ten_cat = TenCategories.query.all()
        hun_cat = HundredCategories.query.all()

        start = 0
        stop = 10
        for i in ten_cat:
            i.hundred_values = hun_cat[start:stop]
            db.session.add(i)

            start += 10
            stop += 10
        db.session.commit()
        return

    def populate_hundred_classes():
        hun_cat = HundredCategories.query.all()
        thou_cat = ThousandCategories.query.all()

        start = 0
        stop = 10
        for i in hun_cat:
            i.thousand_values = thou_cat[start:stop]
            db.session.add(i)

            start += 10
            stop += 10
        db.session.commit()
        return

    populate_ten_classes()
    populate_hundred_classes()



"""Cleanup ISBN numbers"""
# book_instance.isbn = clean_isbn(book_instance.isbn)
# book_instance.isbn13 = clean_isbn(book_instance.isbn13)


# def clean_isbn(isbn):
#     filter_isbn = re.findall("[a-zA-Z0-9]", isbn)
#     join_isbn = ("").join(filter_isbn)
#     return join_isbn


# -----------------------------------------------------------------------------------------------
# One time upload of categories, Admin only


@api.route("/category/ten/upload", methods=["GET", "POST"])
def csv_import_ten_categories():
    if request.method == "POST":

        def category_init_func(row):
            category_instance = TenCategories()
            category_instance.call_number = row["call_number"]
            category_instance.classification = row["classification"]

            return category_instance

        mapdict = {
            "Call Number": "call_number",
            "Classification": "classification",
        }

        request.isave_to_database(
            field_name="file",
            session=db.session,
            table=TenCategories,
            initializer=category_init_func,
            mapdict=mapdict,
        )

        return redirect(
            url_for("main.view_books_ten_categories"), code=302)

    return """
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    """


@api.route("/category/hundred/upload", methods=["GET", "POST"])
def csv_import_hundred_categories():
    if request.method == "POST":

        def category_init_func(row):
            category_instance = HundredCategories()
            category_instance.call_number = row["call_number"]
            category_instance.classification = row["classification"]

            return category_instance

        mapdict = {
            "Call Number": "call_number",
            "Classification": "classification",
        }

        request.isave_to_database(
            field_name="file",
            session=db.session,
            table=HundredCategories,
            initializer=category_init_func,
            mapdict=mapdict,
        )

        return redirect(
            url_for("main.view_books_hundred_categories"), code=302)

    return """
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    """


@api.route("/category/thousand/upload", methods=["GET", "POST"])
def csv_import_thousand_categories():
    if request.method == "POST":

        def category_init_func(row):
            category_instance = ThousandCategories()
            category_instance.call_number = row["call_number"]
            category_instance.classification = row["classification"]

            return category_instance

        mapdict = {
            "Call Number": "call_number",
            "Classification": "classification",
        }

        request.isave_to_database(
            field_name="file",
            session=db.session,
            table=ThousandCategories,
            initializer=category_init_func,
            mapdict=mapdict,
        )
        return redirect(
            url_for("main.view_books_thousand_categories"), code=302)

    return """
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    """
