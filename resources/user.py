import csv
import io
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from models import User, Book
from schemas import UserSchema, BookSchema
from db import db

blp = Blueprint("Users", "users", description="Operations on users")

@blp.route('/user/<int:user_id>')
class User(MethodView):
    @blp.arguments(200, UserSchema)
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        if not user:
            abort(404, message="User not found")
        return user

@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if User.query.filter(User.name == user_data["name"]).first():
            abort(409, messsage="A user with that name already exists")
        kristen = User(name='kristen')
        db.session.add(kristen)
        db.session.commit()

        return {"message": "User created successfully."}, 201

@blp.route('/users/<int:user_id>/books')
def post():
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


# @blp.route('/users/<int:user_id>/circle-packing')
    # @blp.arguments(200, user_id)
    # @blp.response(CirclePackingResponseSchema)
    # def circle_packing(self, user_id):
    #     user = User.query.get(user_id)
    #     if user is None:
    #         abort(404, message="User not found")

    #     books = Book.query.filter_by(user_id=user.id).all()
    #     book_data = [BookSchema().dump(book) for book in books]
    #     packing_data = create_circle_packing(book_data)
    #     return {'packing_data': packing_data}



# @blp.route("/item/<string:item_id>")
# class Item(MethodView):

#     @blp.response(200, ItemSchema)
#     def get(self, item_id):
#         item = ItemModel.query.get_or_404(item_id)
#         return item

#     def delete(self, item_id):
#         item = ItemModel.query.get_or_404(item_id)
#         db.session.delete(item)
#         db.session.commit()
#         return {"message": "Item deleted"}

#     @blp.arguments(ItemUpdateSchema)
#     @blp.response(200, ItemSchema)
#     def put(self, item_data, item_id):
#         item = ItemModel.query.get(item_id)
#         if item:
#             item.price = item_data['price']
#             item.name = item_data['name']
#         else:
#             item = ItemModel(id=item_id, **item_data)

#         db.session.add(item)
#         db.session.commit()
#         return item

# @blp.route("/item")
# class ItemList(MethodView):

#     @blp.response(200, ItemSchema(many=True))
#     def get(self):
#         return ItemModel.query.all()

#     @blp.arguments(ItemSchema)
#     @blp.response(201, ItemSchema)
#     def post(self, item_data):
#         item = ItemModel(**item_data)

#         try:
#             db.session.add(item)
#             db.session.commit()
#         except SQLAlchemyError:
#             abort(500, message="An error occured while inserting the item.")
#         return item
