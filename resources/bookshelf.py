from flask.views import MethodView
from flask_smorest import Blueprint
from flask import jsonify, redirect, url_for
import math

from models import (
    User,
    Book,
    DeweyLevel_1,
    DeweyLevel_2,
    DeweyLevel_3,
)

blp = Blueprint("bookshelf", __name__, description="Circle Packing of User's Books")


@blp.route("/user/<int:user_id>")
class BookShelfView(MethodView):

    def get(self, user_id):
        bookshelf_options = {
            "circle-packing": {"url": url_for("bookshelf.CirclePackingView", user_id=user_id, _external=True)},
            "linear-bookshelf": {"url": url_for("bookshelf.LinearBookShelfView", user_id=user_id, _external=True)},
        }
        return bookshelf_options


@blp.route("linear-bookshelf/user/<int:user_id>")
class LinearBookShelfView(MethodView):

    @blp.response(200)
    @blp.doc(description="Get the linear bookshelf for a user")
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        user_books = []
        for book in user.books:
            book_info = {
                "title": book.title,
                "author": book.author,
                "dewey_decimal": book.dewey_decimal,
            }
            user_books.append(book_info)

        user_books_sorted = sorted(user_books, key=lambda book: book["dewey_decimal"])
        return user_books_sorted

@blp.route("linear-bookshelf/level_1/user/<int:user_id>")
class LinearBookShelfViewLevel1(MethodView):

    @blp.response(200)
    @blp.doc(description="Get the linear bookshelf for a user: Level 1")
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        user_books = []
        levels = DeweyLevel_1.query.all()
        for level in levels:
            level_info = {
                "code": level.code,
                "description": level.description,
                "books": []
            }
            unsorted_books = []
            for book in user.books:
                book_code = get_level_1_info(book)
                if book_code == level.code:
                    book_info = {
                        "title": book.title,
                        "author": book.author,
                        "dewey_decimal": book.dewey_decimal,
                    }
                    unsorted_books.append(book_info)
            user_books_sorted = sorted(unsorted_books, key=lambda book_info: book_info["dewey_decimal"])
            level_info["books"].append(user_books_sorted)
            user_books.append(level_info)

        return user_books


@blp.route("linear-bookshelf/level_2/user/<int:user_id>")
class LinearBookShelfViewLevel2(MethodView):

    @blp.response(200)
    @blp.doc(description="Get the linear bookshelf for a user: Level 2")
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        user_books = []
        levels = DeweyLevel_2.query.all()
        for level in levels:
            level_info = {
                "code": level.code,
                "description": level.description,
                "books": []
            }
            unsorted_books = []
            for book in user.books:
                book_code = get_level_2_info(book)
                if book_code == level.code:
                    book_info = {
                        "title": book.title,
                        "author": book.author,
                        "dewey_decimal": book.dewey_decimal,
                    }
                    unsorted_books.append(book_info)
            user_books_sorted = sorted(unsorted_books, key=lambda book_info: book_info["dewey_decimal"])
            level_info["books"].append(user_books_sorted)
            user_books.append(level_info)
            user_books_total_sorted = sorted(user_books, key=lambda level: level["code"])

        return user_books_total_sorted


@blp.route("linear-bookshelf/level_3/user/<int:user_id>")
class LinearBookShelfViewLevel3(MethodView):

    @blp.response(200)
    @blp.doc(description="Get the linear bookshelf for a user: Level 3")
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        user_books = []
        levels = DeweyLevel_3.query.all()
        for level in levels:
            level_info = {
                "code": level.code,
                "description": level.description,
                "books": []
            }
            unsorted_books = []
            for book in user.books:
                # book_code = get_level_2_info(book)
                if book.dewey_decimal == level.code:
                    book_info = {
                        "title": book.title,
                        "author": book.author,
                        "dewey_decimal": book.dewey_decimal,
                    }
                    unsorted_books.append(book_info)
            user_books_sorted = sorted(unsorted_books, key=lambda book_info: book_info["dewey_decimal"])
            level_info["books"].append(user_books_sorted)
            user_books.append(level_info)
            user_books_total_sorted = sorted(user_books, key=lambda level: level["code"])

        return user_books_total_sorted


@blp.route("circlepacking/user/<int:user_id>")
class CirclePackingView(MethodView):

    def get(self, user_id):
        bookshelf = create_circle_packing(user_id)

        return bookshelf


def create_circle_packing(user_id):

    user = User.query.filter_by(id=user_id).first()
    bookshelf_data = {"name": "Bookshelf", "children": []}

    ten_categories = DeweyLevel_1.query.all()
    for ten_category in ten_categories:
        ten_categories_dict = {
            "name": ten_category.description,
            "code": ten_category.code,
            "value": 4,
            "children": [],
        }
        hundred_categories = DeweyLevel_2.query.filter_by(
            level_1_id=ten_category.id
        ).all()
        for hundred_category in hundred_categories:
            hundred_categories_dict = {
                "name": hundred_category.description,
                "code": hundred_category.code,
                "value": 3,
                "children": [],
            }
            thousand_categories = DeweyLevel_3.query.filter_by(
                level_2_id=hundred_category.id
            ).all()
            for thousand_category in thousand_categories:
                thousand_categories_dict = {
                    "name": thousand_category.description,
                    "code": thousand_category.code,
                    "level_2_id": thousand_category.level_2_id,
                    "value": 2,
                    "children": [],
                }

                # query all user's books in that SPECIFIC dewey decimal category and append
                books = [
                    book
                    for book in user.books
                    if book.dewey_decimal == thousand_category.code
                ]
                if books:
                    for book in books:
                        book_dict = {
                            "title": book.title,
                            "author": book.author,
                            "dewey_decimal": book.dewey_decimal,
                            "value": 1,
                        }
                    thousand_categories_dict["children"].append(book_dict)
                hundred_categories_dict["children"].append(thousand_categories_dict)
            ten_categories_dict["children"].append(hundred_categories_dict)
        bookshelf_data["children"].append(ten_categories_dict)

    return bookshelf_data

def get_level_1_info(book):
    value = float(book.dewey_decimal)
    book_level_1_value = math.floor(value/100.0) * 100
    # level_1 = DeweyLevel_1.query.filter_by(code=book_level_1_value).first()
    return book_level_1_value #, level_1.description
def get_level_2_info(book):
    value = float(book.dewey_decimal)
    book_level_2_value = math.floor(value/10.0) * 10
    return book_level_2_value #, level_1.description
# def get_level_3_info(book):
#     value = float(book.dewey_decimal)
#     book_level_1_value = math.floor(value/100.0) * 100
#     return book_level_1_value #, level_1.description
