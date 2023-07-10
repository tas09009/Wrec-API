from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


from db import db
from models import Book

from schemas import BookSchema

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

    @blp.response(200, BookSchema)
    def get(self, book_id):
        book = Book.query.get_or_404(book_id)
        return book

    def delete(self, book_id):
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return {"message": f"Book id {book.id} (title: {book.title}) deleted"}

