# validation for requests (JSON payload) and responses
from marshmallow import Schema, fields


class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class PlainBookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Str()
    dewey_decimal = fields.Int()
    isbn = fields.Str()

class UserSchema(PlainUserSchema):
    books = fields.List(fields.Nested(PlainBookSchema()), many=True, dump_only=True)
class BookSchema(PlainBookSchema):
    users = fields.List(fields.Nested(PlainUserSchema()), many=True, dump_only=True)

class UserAndBookSchema(Schema):
    # message = fields.Str()
    # user = fields.Nested(UserSchema)
    # book = fields.Nested(BookSchema)

    title = fields.Str()
    author = fields.Str()

