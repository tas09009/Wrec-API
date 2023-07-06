import os

from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

from db import db
from resources.user import blp as UserBlueprint
from resources.auth import blp as AuthBlueprint
from resources.book import blp as BookBlueprint
from resources.bookshelf import blp as BookShelfBlueprint


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Wrec API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app)

    db.init_app(app) # connects app to SQLalchemy
    migrate = Migrate(app, db)
    api = Api(app)

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(BookBlueprint)
    api.register_blueprint(BookShelfBlueprint, url_prefix="/bookshelf")
    api.register_blueprint(AuthBlueprint, url_prefix="/login")

    return app
