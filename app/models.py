from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_serialize import FlaskSerializeMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db
from . import login_manager
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })
Base = declarative_base(metadata=meta)


bookshelf = db.Table('bookshelf', 
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    books = db.relationship('Book',
                            secondary=bookshelf,
                            backref=db.backref('users', lazy='dynamic'),
                            lazy='dynamic')


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                        expires_in=expiration)
        return s.dumps({'id' : self.id}).decode('utf-8')
    
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def get_books_list(self): # not being used
        book_list = [i for i in self.books]


    def __repr__(self):
        return '<User %r>' % self.username


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)

    ''' Classify API + DDC Table '''
    classify_ddc = db.Column(db.String) # rename to dewey_number
    classify_category = db.Column(db.String) # replace later with 3 other tables
    classify_ten_id = db.Column(db.Integer, db.ForeignKey('ten_categories_ddc.id')) # All 3 below were strings, forced to convert
    classify_hundred_id = db.Column(db.Integer, db.ForeignKey('hundred_categories_ddc.id'))
    classify_thousand_id = db.Column(db.Integer, db.ForeignKey('thousand_categories_ddc.id'))

    ''' Goodreads info from csv import '''
    title = db.Column(db.String)
    author = db.Column(db.String)
    isbn = db.Column(db.String)
    isbn13 = db.Column(db.String)


    def __init__(self, title, author, isbn, isbn13):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.isbn13 = isbn13

    def __repr__(self):
        return '<Book %r>' % self.title

    def serialize(self):
        # category_ten = TenCategories.query.filter_by(id=self.classify_ten_id).first()
        # category_ten + "|" + category_ten.classification
        book_user = {
            'title' : self.title,
            'author' : self.author,
            'classify_DDC' : self.classify_ddc,
            'classify_ten_id' : self.classify_ten_id,
            'classify_hundred_id' : self.classify_hundred_id,
            'classify_thousand_id' : self.classify_thousand_id,
            'isbn' : self.isbn,
            'isbn13' : self.isbn13
        }
        return book_user




class TenCategories(db.Model):
    __tablename__ = 'ten_categories_ddc'
    id = db.Column(db.Integer, primary_key=True)
    call_number = db.Column(db.String) # Should be a different data type
    classification = db.Column(db.String)
    hundred_values = db.relationship('HundredCategories', backref='hundred_ten_categories')
    books = db.relationship('Book', backref='classify_ten')



    def to_json(self):
        books = {
            'call_number' : self.call_number,
            'classification' : self.classification,
            'books' : []
        }
        
        return books

class HundredCategories(db.Model):
    __tablename__ = 'hundred_categories_ddc'
    id = db.Column(db.Integer, primary_key=True)
    call_number = db.Column(db.String)
    classification = db.Column(db.String)
    tens_id = db.Column(db.Integer, db.ForeignKey('ten_categories_ddc.id'))
    thousand_values = db.relationship('ThousandCategories', backref='thousand_ten_categories')
    books = db.relationship('Book', backref='classify_hundred')
   
    def to_json(self):
        books = {
            'call_number' : self.call_number,
            'classification' : self.classification,
            'books' : []
        }
        return books

class ThousandCategories(db.Model):
    __tablename__ = 'thousand_categories_ddc'
    id = db.Column(db.Integer, primary_key=True)
    call_number = db.Column(db.String)
    classification = db.Column(db.String)
    hundreds_id = db.Column(db.Integer, db.ForeignKey('hundred_categories_ddc.id'))
    books = db.relationship('Book', backref='classify_thousand')


    def to_json(self):
        books = {
            'call_number' : self.call_number,
            'classification' : self.classification,
            'books' : []
        }
        return books



