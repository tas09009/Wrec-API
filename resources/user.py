from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError

from models import User, Book
# from schemas import UserSchema, BookSchema, CirclePackingResponseSchema
from db import db

blp = Blueprint(
    'circle_packing', 'circle_packing', url_prefix='/circle-packing'
)


@blp.route('/users/<int:user_id>/circle-packing')
class CirclePackingView(MethodView):

    @blp.arguments(200, user_id)
    def circle_packing(self, user_id):
        return {"message": "returning user's circle packing data"}

    # @blp.arguments(200, user_id)
    # @blp.response(CirclePackingResponseSchema)
    # def circle_packing(self, user_id):
    #     user = User.query.get(user_id)
    #     if user is None:
    #         abort(404, message="User not found")

    #     books = Book.query.filter_by(user_id=user.id).all()
    #     book_data = [BookSchema().dump(book) for book in books]
    #     packing_data = create_circle_packing(book_data)
    #     return {'packing_data': packing_data}



# @blp.route("/item/<string:item_id>")
# class Item(MethodView):

#     @blp.response(200, ItemSchema)
#     def get(self, item_id):
#         item = ItemModel.query.get_or_404(item_id)
#         return item

#     def delete(self, item_id):
#         item = ItemModel.query.get_or_404(item_id)
#         db.session.delete(item)
#         db.session.commit()
#         return {"message": "Item deleted"}

#     @blp.arguments(ItemUpdateSchema)
#     @blp.response(200, ItemSchema)
#     def put(self, item_data, item_id):
#         item = ItemModel.query.get(item_id)
#         if item:
#             item.price = item_data['price']
#             item.name = item_data['name']
#         else:
#             item = ItemModel(id=item_id, **item_data)

#         db.session.add(item)
#         db.session.commit()
#         return item

# @blp.route("/item")
# class ItemList(MethodView):

#     @blp.response(200, ItemSchema(many=True))
#     def get(self):
#         return ItemModel.query.all()

#     @blp.arguments(ItemSchema)
#     @blp.response(201, ItemSchema)
#     def post(self, item_data):
#         item = ItemModel(**item_data)

#         try:
#             db.session.add(item)
#             db.session.commit()
#         except SQLAlchemyError:
#             abort(500, message="An error occured while inserting the item.")
#         return item
