from db import db
from .user_book import user_book

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    books = db.relationship('Book', secondary=user_book, back_populates='users', lazy=True)
