from db import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    #TODO: unique contraint is not working, I added multiple taniyas
    name = db.Column(db.String(128), unique=True, nullable=False)
    books = db.relationship('Book', back_populates='users', secondary="users_books", lazy=True, cascade="all, delete")