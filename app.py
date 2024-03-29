import os

from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
from extensions import bcrypt
from dotenv import load_dotenv

from db import db
from resources.user import blp as UserBlueprint
from resources.auth import blp as AuthBlueprint
from resources.book import blp as BookBlueprint
from resources.bookshelf import blp as BookShelfBlueprint
from resources.uploads import blp as ImportDataBlueprint
from models import User


login_manager = LoginManager()

@login_manager.user_loader
def load_use(user_id):
    return User.query.get(int(user_id))

def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    flask_env = os.getenv("FLASK_ENV", "development")
    if flask_env == 'production':
        database_url = os.getenv("DATABASE_URL_PROD")
    elif flask_env == 'testing':
        database_url = os.getenv("DATABASE_URL_TEST")
    else:
        database_url = os.getenv("DATABASE_URL_DEV")

    if not database_url:
        raise ValueError("Database URL is not set.")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Wrec API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app)

    db.init_app(app) # connects app to SQLalchemy
    migrate = Migrate(app, db)
    api = Api(app)

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(BookBlueprint, url_prefix="/book")
    api.register_blueprint(BookShelfBlueprint, url_prefix="/bookshelf")
    api.register_blueprint(AuthBlueprint, url_prefix="/login")
    api.register_blueprint(ImportDataBlueprint, url_prefix="/upload")

    return app
