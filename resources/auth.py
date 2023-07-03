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
    "facebook" : {"lable": "Sign in with Facebook", "url": "/login/facebook", "button_value" : 0},
    "amazon" : {"lable": "Sign in with Amazon", "url": "/login/amazon", "button_value" : 1},
    "apple" : {"lable": "Sign in with Apple", "url": "/login/apple", "button_value" : 2},
    "google" : {"lable": "Sign in with Google", "url": "/login/google", "button_value" : 4},
    "goodreads" : {"lable": "Sign in with Goodreads Email", "url": "/login/goodreads_email", "button_value" : 3},
}

@blp.route("/")
class UserLogin(MethodView):

    def get(self):
        return jsonify(login_options)


@blp.route("/facebook")
class UserLoginFacebook(MethodView):
    @blp.arguments(
        UserSchema, location="json" # data will be in json, not url
    )  # Update the user schema to accept password
    def post(self, user_data):
        login_buttons, browser = get_login_links()

        # Specific Login
        button_idx = login_options.get("facebook").get("button_value")
        user_id, browser = facebook_sign_in(login_buttons, button_idx, browser, user_data)
        return finish_login(user_id, user_data, browser)

@blp.route("/amazon")
class UserLoginAmazon(MethodView):
    @blp.arguments(
        UserSchema, location="json" # data will be in json, not url
    )  # Update the user schema to accept password
    def post(self, user_data):
        login_buttons, browser = get_login_links()

        # Specific Login
        button_idx = login_options.get("amazon").get("button_value")
        user_id, browser = amazon_sign_in(login_buttons, button_idx, browser, user_data)
        return finish_login(user_id, user_data, browser)

@blp.route("/apple")
class UserLoginApple(MethodView):
    @blp.arguments(
        UserSchema, location="json" # data will be in json, not url
    )  # Update the user schema to accept password
    def post(self, user_data):
        login_buttons, browser = get_login_links()

        # Specific Login
        button_idx = login_options.get("apple").get("button_value")
        user_id, browser = apple_sign_in(login_buttons, button_idx, browser, user_data)
        return finish_login(user_id, user_data, browser)

@blp.route("/google")
class UserLoginGoogle(MethodView):
    @blp.arguments(
        UserSchema, location="json" # data will be in json, not url
    )  # Update the user schema to accept password
    def post(self, user_data):
        login_buttons, browser = get_login_links()

        # Specific Login
        button_idx = login_options.get("google").get("button_value")
        user_id, browser = google_sign_in(login_buttons, button_idx, browser, user_data)
        return finish_login(user_id, user_data, browser)

@blp.route("/goodreads_email")
class UserLoginGoodReads(MethodView):
    @blp.arguments(
        UserSchema, location="json" # data will be in json, not url
    )  # Update the user schema to accept password
    def post(self, user_data):
        login_buttons, browser = get_login_links()

        # Specific Login
        button_idx = login_options.get("goodreads").get("button_value")
        user_id, browser = goodreads_sign_in(login_buttons, button_idx, browser, user_data)
        return finish_login(user_id, user_data, browser)

def finish_login(user_id, user_data, browser):
    email = user_data.get("email")
    # password = user_data.get("password")
    name = user_data.get("name")
    user = User.query.filter_by(email=email).first()
    if user:
        return redirect(url_for("bookshelf.BookShelfView", user_id=user.id))

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
    return redirect(url_for("bookshelf.BookShelfView", user_id=new_user.id))



# -------------------------------------------------------------------------
# from flask_dance.consumer import OAuth2ConsumerBlueprint, oauth_authorized, oauth_error
# from flask_smorest import Blueprint, abort
# from flask.views import MethodView
# import requests


# # Amazon OAuth configuration
# client_id = "amzn1.application-oa2-client.c7cf91a7a14e4617b2219160850b0ee2"
# client_secret = "amzn1.oa2-cs.v1.ecf9473f1ba98315a023e2e24dcef03fe0f3850bcfa89abe22b40a9b4c1d17f9"
# authorization_url = "https://www.amazon.com/ap/oa"
# token_url = "https://api.amazon.com/auth/o2/token"
# redirect_url = "https://127.0.0.1:5001/token"

# amazon_blueprint = OAuth2ConsumerBlueprint(
#     "amazon",
#     __name__,
#     client_id=client_id,
#     client_secret=client_secret,
#     authorization_url=authorization_url,
#     token_url=token_url,
#     redirect_url=redirect_url,
#     scope=["profile"],
#     response_type=["code"],
#     # "scope": "profile",
#     # authorization_kwargs={"response_type": "code"},
# )

# blp = Blueprint("UsersLogin", __name__, description="Authenticate users")

# amazon_params = {
#     "client_id": client_id,
#     "scope": "profile",
#     "response_type": "code",
#     "redirect_uri": redirect_url,
# }
# # amazon_auth_str = authorization_url + urlencode(amazon_params)
# amazon_auth_str = f"{authorization_url}?client_id={client_id}&scope=profile&response_type=code&redirect_uri={redirect_url}"


# @blp.route("/callback")
# class AmazonCallbackResource(MethodView):

#     # @blp.response(200, "Success")
#     def get(self):
#         if not amazon_blueprint.session.authorized:
#             abort(401, message="Authorization failed.")

#         # Get the access token using the authorization code
#         amazon_blueprint.session.fetch_token(
#             token_url=token_url,
#             authorization_response=requests.request.url,
#         )

#         # Make a request to the user profile endpoint
#         response = amazon_blueprint.session.get("/user/profile")
#         if response.ok:
#             profile_data = response.json()
#             return profile_data
#         else:
#             abort(500, message="Failed to retrieve user profile.")

