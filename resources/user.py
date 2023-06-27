"""
[x] Save CSV file using Amazon login
[x] Encapsulate all logic into functions
[x] Log into Goodreads and download a csv file
"""

from flask import redirect, url_for
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import User, Book
from schemas import UserSchema
from goodreads_scrape import get_login_links, sign_in, transfer_session, export_book


blp = Blueprint("Users", __name__, description="Operations on users")

@blp.route('/user/<int:user_id>')
class UserView(MethodView):

    # @blp.arguments(PlainUserSchema)
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return user

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


@blp.route('/login')
class UserLogin(MethodView):

    @blp.arguments(UserSchema, location="json") # Update the user schema to accept password
    def post(self, user_data):
        buttons, browser = get_login_links()
        user_id, user = sign_in(buttons, browser, user_data)

        # Sign in
        user = User.query.filter_by(email=user_data["email"]).first()
        if not user:
            new_user = User(email=user_data["email"], name=user_data["name"]) # Should be user = User(**user_data)
            try:
                db.session.add(new_user)
                db.session.commit()
            except IntegrityError:
                abort(400, message="User with that name already exists")
            except SQLAlchemyError as e:
                abort(500, message=str(e))

        session = transfer_session(browser)
        export_book(session, user_id, user)

        # TODO: populate dewey decimal values for all the books uploaded

        user_redirect = user or new_user
        return redirect(url_for("blp.bookshelf", user_id=user_redirect.id))
        # return {"message": f"Successfully downloaded all books into a csv_file for user_id: {user_id}", "redirect link": f"/bookshelf/user/<int:user_id>"}
