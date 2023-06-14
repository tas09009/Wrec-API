import csv
import io
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import User, Book
from schemas import UserSchema

blp = Blueprint("Users", __name__, description="Operations on users")

@blp.route('/user/<int:user_id>')
class UserView(MethodView):

    # @blp.arguments(PlainUserSchema)
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return user

    #TODO
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": f"User id {user.name} deleted"}

@blp.route('/user')
class UserRegister(MethodView):

    @blp.response(200, UserSchema(many=True))
    def get(self):
        return User.query.all()

    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        user = User(**user_data)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(400, message="User with that name already exists")
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return user


@blp.route("/user/<string:user_id>/book/<string:book_id>")
class LinkBooktoUser(MethodView):

    @blp.response(201, UserSchema)
    def post(self, user_id, book_id):
        user = User.query.get_or_404(user_id)
        book = Book.query.get_or_404(book_id)

        user.books.append(book)
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while adding a book to the user")
        return user


#TODO
# @blp.route('/users/<int:user_id>/books')
# def post():
#     with open("goodreadsKirstenKorevaar_sample.csv") as csv_file:
#         reader = csv.DictReader(csv_file)

#         for row in reader:
#             book = Book(
#                 title=row['Title'],
#                 author=row['Author'],
#                 isbn=row['ISBN'],
#                 value=1,
#                 user_id=user.id
#             )
#             db.session.add(book)
#             db.session.commit()

#     print("Successfully uploaded all books")
#     return {"message": "Successfully uploaded all books"}
