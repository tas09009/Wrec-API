from db import db

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    author = db.Column(db.String(128), unique=False)
    dewey_decimal = db.Column(db.Integer())
    isbn = db.Column(db.String(16))
    users = db.relationship('User', back_populates='books', secondary="users_books", lazy=True, cascade="all, delete")
    value = 1
    # users = db.relationship('User', secondary="user_book", back_populates='books', lazy=True)

# user_book = db.Table('user_book',
#     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
#     db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
# )