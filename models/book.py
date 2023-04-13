from db import db
from .user_book import user_book

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    author = db.Column(db.String(128), unique=False)
    dewey_decimal = db.Column(db.Integer())
    isbn = db.Column(db.String(16))
    users = db.relationship('User', secondary=user_book, back_populates='books', lazy=True)
    value = 1