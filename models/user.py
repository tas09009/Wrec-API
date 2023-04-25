from db import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    #TODO: unique contraint is not working, I added multiple taniyas
    name = db.Column(db.String(128), unique=True, nullable=False)
    books = db.relationship('Book', back_populates='users', secondary="users_books", lazy=True, cascade="all, delete")
    # books = db.relationship('Book', secondary="user_book", back_populates='users', lazy=True)

# user_book = db.Table('user_book',
#     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
#     db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
# )