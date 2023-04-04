from db import db

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), unique=False, nullable=False)
    book = db.relationship("BookModel", back_populates="users")
