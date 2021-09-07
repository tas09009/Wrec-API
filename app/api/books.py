from urllib.request import urlopen
from urllib.parse import urlencode
import re

from flask import request, redirect, url_for
import flask_excel as excel  # not being used?
import xmltodict

from app.models import (
    Book,
    User,
    TenCategories,
    HundredCategories,
    ThousandCategories,
)
from . import api
from .. import db


# Add ['DELETE'] method. Doesn't remove book info, only user association


# http://127.0.0.1:5000/api/v1/books/upload
@api.route("/books/upload", methods=["GET", "POST"])
def csv_import():
    if request.method == "POST":

        def book_init_func(row):
            book_instance = Book(row["title"])
            book_instance.author = row["author"]
            book_instance.isbn = row["isbn"]
            book_instance.isbn13 = row["isbn13"]

            """Cleanup ISBN numbers"""
            # book_instance.isbn = clean_isbn(book_instance.isbn)
            # book_instance.isbn13 = clean_isbn(book_instance.isbn13)

            """Add rows to User.books"""
            user = User.query.filter_by(username="john").first()
            user.books.append(book_instance)

            return book_instance

        mapdict = {
            "Title": "title",
            "Author": "author",
            "ISBN": "isbn",
            "ISBN13": "isbn13",
        }

        request.isave_to_database(
            field_name="file",
            session=db.session,
            table=Book,
            initializer=book_init_func,
            mapdict=mapdict,
        )

        """Create Ten and Hundred nested relationship"""
        ten_and_hundred()

        """Dewey Number + Category"""
        dewey_and_thousand()

        return redirect(
            url_for("main.view_books_by_user", username="john"), code=302
        )

    return """
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    """


def dewey_and_thousand():
    user = User.query.filter_by(username="john").first()
    books = user.books.all()
    for book_instance in books:
        book_instance.classify_ddc = request_book_data(book_instance.isbn)

        db.session.add(book_instance)
        db.session.commit()

        book_instance.classify_ten_id = dewey_to_category_ten(
            book_instance.classify_ddc
        )
        book_instance.classify_hundred_id = dewey_to_category_hundred(
            book_instance.classify_ddc
        )
        book_instance.classify_thousand_id = dewey_to_category_thousand(
            book_instance.classify_ddc
        )

        if book_instance.classify_ten_id:
            category_obj = TenCategories.query.filter_by(
                id=book_instance.classify_ten_id
            ).first()
            category_obj.books.append(book_instance)
            db.session.add(category_obj)
            db.session.commit()
        if book_instance.classify_hundred_id:
            category_obj = HundredCategories.query.filter_by(
                id=book_instance.classify_hundred_id
            ).first()
            category_obj.books.append(book_instance)
            db.session.add(category_obj)
            db.session.commit()
        if book_instance.classify_thousand_id:
            category_obj = ThousandCategories.query.filter_by(
                id=book_instance.classify_thousand_id
            ).first()
            category_obj.books.append(book_instance)
            db.session.add(category_obj)
            db.session.commit()

        db.session.add(book_instance)  # ?? Redundant with add + commit above?
        db.session.commit()
    return


def ten_and_hundred():
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


# isbn to Dewey decimal
@api.route("/dewey/", methods=["GET"])
def request_book_data(isbn):
    """Classify API from ISBN -> JSON of book"""

    if isbn:

        base = "http://classify.oclc.org/classify2/Classify?"
        summaryBase = "&summary=true"
        parm_type = "isbn"
        parm_value = isbn
        search_url = (
            base
            + urlencode({parm_type: parm_value.encode("utf-8")})
            + summaryBase
        )
        xml_content = urlopen(
            search_url
        ).read()  # TODO use requests library instead. Also use response codes
        xmlDict = xmltodict.parse(xml_content)

        isbnDirect = isbn_to_dewey(xmlDict)
        return isbnDirect

    elif isbn is None:
        return "No ISBN provided"


def isbn_to_dewey(xmlDict):

    if xmlDict.get("classify").get("response").get("@code") == "0":
        try:
            dewey_number = (
                xmlDict.get("classify")
                .get("recommendations")
                .get("ddc")
                .get("mostPopular")
                .get("@sfa")
            )
            return dewey_number
        except AttributeError:
            return "Returned book response, but has no dewey number"
    
    elif xmlDict.get("classify").get("response").get("@code") == "4":
        try:
            owi_number = (
                xmlDict.get("classify").get("works").get("work")[0].get("@owi")
            )

            base = "http://classify.oclc.org/classify2/Classify?"
            parm_type = "owi"
            parm_value = owi_number
            search_url = base + urlencode(
                {parm_type: parm_value.encode("utf-8")}
            )
            xml_content = urlopen(search_url).read()
            xmlDict = xmltodict.parse(xml_content)

            dewey_number = (
                xmlDict.get("classify")
                .get("recommendations")
                .get("ddc")
                .get("mostPopular")
                .get("@sfa")
            )
            return dewey_number
        except AttributeError:
            return "multiple works found, use OWI"
    else:
        return "Key Error"


"""Find the corresponding Category titles"""


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


def clean_isbn(isbn):
    filter_isbn = re.findall("[a-zA-Z0-9]", isbn)
    join_isbn = ("").join(filter_isbn)
    return join_isbn


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
            url_for("main.view_books_ten_categories", username="john"),
            code=302,
        )

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
            url_for("main.view_books_hundred_categories", username="john"),
            code=302,
        )

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
            url_for("main.view_books_thousand_categories", username="john"),
            code=302,
        )

    return """
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    """
