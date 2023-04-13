# validation for requests (JSON payload) and responses
from marshmallow import Schema, fields



# class BookSchema(Schema):
#     id = fields.Int()
#     title = fields.Str()
#     dewey_decimal = fields.Str()


class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str()


# class CirclePackingResponseSchema(Schema):
#     packing_data = fields.Dict()





#     books = fields.List(fields.Nested(BookSchema))