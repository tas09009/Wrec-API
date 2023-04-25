from db import db

class UsersBooks(db.Model):
    __tablename__ = "users_books"
    id = db.Column(db.Integer, primary_key=True)
    users = db.Column(db.Integer, db.ForeignKey("users.id"))
    books = db.Column(db.Integer, db.ForeignKey("books.id"))

# user_book = db.Table('user_book',
#     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
#     db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
# )