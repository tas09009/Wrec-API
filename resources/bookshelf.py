# from flask.views import MethodView
# from flask_smorest import Blueprint, abort
# from models import Bookshelf
# from schemas import BookshelfSchema

# blp = Blueprint('bookshelf', __name__, url_prefix='/api/v1/bookshelves', description="Operations on User's bookshelf")

# @blp.route("/<int:bookshelf_id>")
# class BookshelfAPI(MethodView):

#     @blp.response(200, BookshelfSchema)
#     def get(self, bookshelf_id):
#         bookshelf = Bookshelf.query.get_or_404(bookshelf_id)
#         return bookshelf
