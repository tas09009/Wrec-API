from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_login import login_user, logout_user

from db import db
from models import User, Book
from schemas import UserLoginSchema, UserSchema


blp = Blueprint("users", __name__, description="Operations on users")


@blp.route('/login')
class UserLoginView(MethodView):
    @blp.arguments(UserLoginSchema)
    @blp.response(200)
    def post(self, user_data):
        email = user_data.get('email')
        password = user_data.get('password')
        user = User.authenticate(email, password)
        if user:
            login_user(user)
            return {"message": "Logged in successfully"}, 200
        return {
                "message": "Invalid email or password. If you do not have an account, please register.",
                "error_code": "user_not_found"
            }, 400

@blp.route('/logout')
class UserLogoutView(MethodView):
    def get(self):
        logout_user()
        return {"message": "Logged out successfully"}

@blp.route('/register')
class UserRegisterView(MethodView):
    @blp.arguments(UserLoginSchema)
    @blp.response(201)
    def post(self, user_data):
        email = user_data.get('email')
        password = user_data.get('password')
        new_user = User(email=email)
        new_user.set_password(password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return {"message": "Registered Successfully"}, 201
        except IntegrityError:
            abort(400, message="Incorrect email or password")
        except SQLAlchemyError as e:
            abort(500, message=str(e))


@blp.route("/user/<int:user_id>")
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
        return {"message": f"User {user.email} deleted"}


@blp.route("/user")
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
            abort(400, message="User already exists")
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

