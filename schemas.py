from marshmallow import Schema, fields

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True)
    password = fields.Str(load_only=True)


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
    title = fields.Str()
    author = fields.Str()
