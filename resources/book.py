from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


import csv
from db import db
from models import Book, User

# from models import StoreModel
# from schemas import StoreSchema
from scripts.generate_circle_packing_json import generate_dewey_categories_blueprint

blp = Blueprint("books", __name__, description="Operations on books")


@blp.route('/upload_sample')
class UserBooks(MethodView):
    blp.response(200)
    def get():
        kristen = User.query.filter_by(name="kristen").first()
        if not kristen:
            kristen = User(name='kristen')
            db.session.add(kristen)
            db.session.commit()
        with open("goodreadsKirstenKorevaar_sample.csv") as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                book = Book(
                    title=row['Title'],
                    author=row['Author'],
                    isbn=row['ISBN'],
                    value=1,
                    user_d=kristen.id
                )
                db.session.add(book)
                db.session.commit()

        print("Successfully uploaded all books")
        return {"message": "Successfully uploaded all books"}


# from flask import Flask, jsonify
# from flask_sqlalchemy import SQLAlchemy


# @blp.route('/bookshelf/<int:user_id>')
# def get_bookshelf(user_id):
#     books = db.session.query(Book).join(User).filter(User.id == user_id).all()
#     data = BookshelfSchema().dump({
#         'name': 'Bookshelf',
#         'children': group_books_by_category(books)
#     })
#     return jsonify(data)


# # OLD
# @blp.route("/bookshelf")
# class BookShelf(MethodView):

#     @blp.response(200)
#     def get(self):
#         return generate_dewey_categories_blueprint()




# @blp.route("/update_books")
# Get latest info from goodreads

# -------------------------------------------------------
# @blp.route("/store/<string:store_id>")
# class Store(MethodView):

#     @blp.response(200, StoreSchema)
#     def get(self, store_id):
#         store = StoreModel.query.get_or_404(store_id)
#         return store

#     def delete(self, store_id):
#         store = StoreModel.query.get_or_404(store_id)
#         db.session.delete(store)
#         db.session.commit()
#         return {"message": "Store deleted"}

# @blp.route("/store")
# class StoreList(MethodView):

#     @blp.response(200, StoreSchema(many=True))
#     def get(self):
#         return StoreModel.query.all()

#     @blp.arguments(StoreSchema)
#     @blp.response(201, StoreSchema)
#     def post(self, store_data):
#         store = StoreModel(**store_data)
#         try:
#             db.session.add(store)
#             db.session.commit()
#         except IntegrityError:
#             abort(400, message="A store with that name already exists")
#         except SQLAlchemyError:
#             abort(500, message="An error occured while inserting the item")
#         return store
