from db import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    phone_number = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(128), unique=True, nullable=False) #TODO: unique contraint is not working, I added multiple taniyas
    books = db.relationship('Book', back_populates='users', secondary="users_books", lazy=True, cascade="all, delete")