from flask.views import MethodView
from flask_smorest import Blueprint
from flask import jsonify, redirect, url_for

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
        # bookshelf_options = {
        #     "circle- packing": {"url": f"circlepacking/user/{user_id}"},
        #     "linear bookshelf": {"url": f"linear-bookshelf/user/{user_id}"},
        # }

        # bookshelf_options = {
        #     "circle-packing": {"url": current_app.api.url_for(self, user_id=user_id, _external=True)},
        #     "linear-bookshelf": {"url": current_app.api.url_for(self, user_id=user_id, _external=True)},
        # }
        bookshelf_options = {
            "circle-packing": {"url": url_for("bookshelf.CirclePackingView", user_id=user_id, _external=True)},
            "linear-bookshelf": {"url": url_for("bookshelf.LinearBookShelfView", user_id=user_id, _external=True)},
        }
        # return redirect(url_for("bookshelf.BookShelfView", user_id=user.id))

        return jsonify(bookshelf_options)

@blp.route("linear-bookshelf/user/<int:user_id>")
class LinearBookShelfView(MethodView):

    @blp.response(200)
    @blp.doc(description="Get the linear bookshelf for a user")
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        # books = user.books.order_by(Book.dewey_decimal.asc()).all()
        books = sorted(user.books, key=lambda book: book.dewey_decimal)

        serialized_books = [book.serialize() for book in books]
        return jsonify(serialized_books)
        return jsonify(books)
        return [book.serialize() for book in books]


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
