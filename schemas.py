# validation for requests (JSON payload) and responses
from marshmallow import Schema, fields



# class BookSchema(Schema):
#     id = fields.Int()
#     title = fields.Str()
#     dewey_decimal = fields.Str()


# class UserSchema(Schema):
#     id = fields.Int()
#     name = fields.Str()
#     books = fields.List(fields.Nested(BookSchema))


# class CirclePackingResponseSchema(Schema):
#     packing_data = fields.Dict()