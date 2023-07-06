from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


import csv
from db import db
from models import Book, User

from schemas import BookSchema
from scripts.generate_circle_packing_json import generate_dewey_categories_blueprint

blp = Blueprint("books", __name__, description="Operations on books")


@blp.route("/book")
class BookView(MethodView):

    @blp.response(200, BookSchema(many=True))
    def get(self):
        return Book.query.all()

    @blp.arguments(BookSchema)
    @blp.response(201, BookSchema)
    def post(self, book_data):
        book = Book(**book_data)
        try:
            db.session.add(book)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A book with that name already exists")
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the book")
        return book

@blp.route("/book/<int:book_id>")
class BookView(MethodView):

    @blp.response(200, BookSchema(many=True))
    def get(self, book_id):
        book = Book.query.get_or_404(book_id)
        return book

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
