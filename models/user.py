from db import db
from flask_login import UserMixin
from extensions import bcrypt

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(128))
    books = db.relationship('Book', back_populates='users', secondary="users_books", lazy=True)
    book_csv = db.relationship('BookCSV', backref='user', uselist=False)

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
