from db import db

class BookModel(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship("UserModel", back_populates="books", lazy="dynamic", cascade="all, delete")