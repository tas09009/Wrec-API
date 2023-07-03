from flask.views import MethodView
from flask_smorest import Blueprint
# from cache import cache

from models import (
    User,
    DeweyLevel_1,
    DeweyLevel_2,
    DeweyLevel_3,
)

blp = Blueprint("bookshelf", __name__, description="Circle Packing of User's Books")


@blp.route("/bookshelf/user/<int:user_id>")
class BookShelfView(MethodView):

    # @cache.cached()
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
