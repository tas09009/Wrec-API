from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint

from db import db
from sqlalchemy import between
from models import User, DeweyDecimalSystem, DeweyLevel_1, DeweyLevel_2, DeweyLevel_3
from schemas import PlainBookSchema, BookSchema

blp = Blueprint('bookshelf', __name__, description="Circle Packing of User's Books")

@blp.route('/bookshelf/user/<int:user_id>')
class BookShelfView(MethodView):

    # @blp.response(200, PlainBookSchema(many=True))
    def get(self, user_id):
        populate_nested_structure()

        bookshelf_data = {
            "name": "Dewey Decimal System",
            "children": []
        }
        return bookshelf_data


#TODO: This will need to go in a flask migration script - dewey_levels.py
def populate_nested_structure():
    """
    nest 100 'HundredCategories' within 10 'TenCategories'
    nest 100 'ThousandCategories' within 10 'HundredCategories'
    """
    start = 1
    stop = 10
    hundred_category_id = 1
    while hundred_category_id <= 100:
        thousand_categories_subgroup = DeweyLevel_3.query.filter(DeweyLevel_3.id.between(start,stop)).all()
        for category in thousand_categories_subgroup:
            category.level_2_id = hundred_category_id
            db.session.add(category)

        start += 10
        stop += 10
        hundred_category_id += 1


    start = 1
    stop = 10
    ten_category_id = 1
    while ten_category_id <= 10:
        hundred_categories_subgroup = DeweyLevel_2.query.filter(DeweyLevel_2.id.between(start,stop)).all()
        for category in hundred_categories_subgroup:
            category.level_1_id = ten_category_id
            db.session.add(category)

        start += 10
        stop += 10
        ten_category_id += 1


    db.session.commit()
    return




def generate_dewey_categories_blueprint():

    dewey_decimal_systems = DeweyDecimalSystem.query.all()

    bookshelf_data = {
        "name": "Dewey Decimal System",
        "children": []
    }

    for dewey_decimal_system in dewey_decimal_systems:
        dewey_data = {
            "name": "Dewey Decimal System",
            "children": []
        }

        for level_1_category in dewey_decimal_system.level_1:
            level_1_data = {
                "name": level_1_category.description,
                "children": []
            }

            for level_2_subcategory in level_1_category.level_2:
                level_2_data = {
                    "name": level_2_subcategory.description,
                    "children": []
                }

                level_1_data["children"].append(level_2_data)

                for level_3_subcategory in level_2_subcategory.level_3:
                    level_3_data = {
                        "name": level_3_subcategory.description,
                        "size": level_3_subcategory.value
                    }

                    level_2_data["children"].append(level_3_data)

            dewey_data["children"].append(level_1_data)

        bookshelf_data["children"].append(dewey_data)

    return jsonify(bookshelf_data)







def get_users_books(user_id):
    user = User.query.get_or_404(user_id)
    user_books = user.books
    book_schema = PlainBookSchema(many=True)
    serialized_books = book_schema.dump(user_books)


    bookshelf_data = {
        "name": "Bookshelf",
        "children":serialized_books,
    }
    return jsonify(bookshelf_data)
