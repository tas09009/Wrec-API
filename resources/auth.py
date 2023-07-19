from flask import redirect, url_for, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import User, Book
from schemas import UserSchema
from goodreads_scrape import get_login_links, transfer_session, export_book
from goodreads_scrape import amazon_sign_in, facebook_sign_in, google_sign_in, apple_sign_in, goodreads_sign_in

blp = Blueprint("Auth", __name__, description="Operations on Authentication")

login_options = {
    "facebook" : {"lable": "Sign in with Facebook", "url": "/login/facebook", "button_value" : 3},
    "amazon" : {"lable": "Sign in with Amazon", "url": "/login/amazon", "button_value" : 0},
    "apple" : {"lable": "Sign in with Apple", "url": "/login/apple", "button_value" : 1},
    "google" : {"lable": "Sign in with Google", "url": "/login/google", "button_value" : 2},
    "goodreads" : {"lable": "Sign in with Goodreads Email", "url": "/login/goodreads_email", "button_value" : 4},
}


@blp.route("/")
class UserLogin(MethodView):

    def get(self):
        return jsonify(login_options)


@blp.route("/logout")
class UserLogin(MethodView):

    def get(self):
        return {"message": "You are now logged out"}


@blp.route("/facebook")
class UserLoginFacebook(MethodView):
    @blp.arguments(
        UserSchema, location="json"
    )
    def post(self, user_data):
        login_buttons, browser = get_login_links()

        # Specific Login
        button_idx = login_options.get("facebook").get("button_value")
        user_id, browser = facebook_sign_in(login_buttons, button_idx, browser, user_data)
        return finish_login(user_id, user_data, browser)

@blp.route("/amazon")
class UserLoginAmazon(MethodView):
    @blp.arguments(
        UserSchema, location="json"
    )
    def post(self, user_data):
        login_buttons, browser = get_login_links()

        # Specific Login
        button_idx = login_options.get("amazon").get("button_value")
        user_id, browser = amazon_sign_in(login_buttons, button_idx, browser, user_data)
        return finish_login(user_id, user_data, browser)

@blp.route("/apple")
class UserLoginApple(MethodView):
    @blp.arguments(
        UserSchema, location="json"
    )
    def post(self, user_data):
        login_buttons, browser = get_login_links()

        # Specific Login
        button_idx = login_options.get("apple").get("button_value")
        user_id, browser = apple_sign_in(login_buttons, button_idx, browser, user_data)
        return finish_login(user_id, user_data, browser)

@blp.route("/google")
class UserLoginGoogle(MethodView):
    @blp.arguments(
        UserSchema, location="json"
    )
    def post(self, user_data):
        login_buttons, browser = get_login_links()

        # Specific Login
        button_idx = login_options.get("google").get("button_value")
        user_id, browser = google_sign_in(login_buttons, button_idx, browser, user_data)
        return finish_login(user_id, user_data, browser)

@blp.route("/goodreads_email")
class UserLoginGoodReads(MethodView):
    @blp.arguments(
        UserSchema, location="json"
    )
    def post(self, user_data):
        login_buttons, browser = get_login_links()

        # Specific Login
        button_idx = login_options.get("goodreads").get("button_value")
        user_id, browser = goodreads_sign_in(login_buttons, button_idx, browser, user_data)
        return finish_login(user_id, user_data, browser)

def finish_login(user_id, user_data, browser): #[ ] user_id here is for goodreads, not User
    email = user_data.get("email")
    name = user_data.get("name")
    user = User.query.filter_by(email=email).first()
    if user:
        return redirect(url_for("bookshelf.LinearBookShelfView", user_id=user.id))

    new_user = User(
        email=email, name=name
    )  # Should be user = User(**user_data)
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        abort(400, message="User with that name already exists")
    except SQLAlchemyError as e:
        abort(500, message=str(e))

    session = transfer_session(browser)
    export_book(session, user_id, new_user)
    return redirect(url_for("bookshelf.LinearBookShelfView", user_id=new_user.id))