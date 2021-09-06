from flask import render_template, jsonify, request, url_for, redirect
from flask_login import login_required, current_user
from . import main
from .. import db
from app.models import Book, User, TenCategories, HundredCategories, ThousandCategories



@main.route('/')
def index():
    return render_template('index.html')

# @main.route('/<username>/books/')
# See missing dewey numbers, not to use during production
@main.route('/<username>/circlepacking')
@login_required
def circle_packing_view():
    user = User.query.filter_by(id=current_user.id).first()


    '''Each of their respective objects'''
    ten_cat = TenCategories.query.all()
    hun_cat = HundredCategories.query.all()
    thou_cat = ThousandCategories.query.all()

    '''Each of their respective classifications'''
    ten_cat_list = [ten_category.classification for ten_category in ten_cat]
    hun_cat_list = [hun_category.classification for hun_category in hun_cat]
    thou_cat_list = [thou_category.classification for thou_category in thou_cat]

    tens_list = []
    
    
    books_dict = {"name" : "books", "children" : tens_list}
    for i in ten_cat:
        ten_placeholder = {} # dict of tens category
        hun_list = []
        ten_title = i.call_number + ' | ' + i.classification # string tens list
        ten_placeholder["name"] = ten_title
        ten_placeholder["children"] = hun_list
        for j in i.hundred_values:
            hun_placeholder = {}
            tho_list = []
            hun_title = j.call_number + ' | ' + j.classification
            hun_placeholder["name"] = hun_title
            hun_placeholder["children"] = tho_list
            hun_list.append(hun_placeholder)
            for k in j.thousand_values:
                tho_placeholder = {}
                book_list = []
                tho_title = k.call_number + ' | ' + k.classification
                tho_placeholder["name"] = tho_title
                tho_placeholder["children"] = [i.title for i in k.books]
                tho_list.append(tho_placeholder)

        tens_list.append(ten_placeholder)
  
    return jsonify(books_dict)


@main.route('/books_uploaded/<username>')
@login_required
def view_books_by_user(username):
    books = User.query.filter_by(username=username).first().books.all()

    books_list = [book.serialize() for book in books]
    return jsonify(books_list)

@main.route('/ten_categories/<username>')
@login_required
def view_books_ten_categories(username):
    books = User.query.filter_by(username=username).first().books.all()
    ten_cat = TenCategories.query.all()

    books_within_categories = [category.to_json() for category in ten_cat]
    return jsonify(books_within_categories)


    # def to_json(self):
    #     books = {
    #         'call_number' : self.call_number,
    #         'classification' : self.classification,
    #         'books' : [book.title for book in self.books]
    #     }
    #     return books

@main.route('/hundred_categories/<username>')
@login_required
def view_books_hundred_categories(username):
    hun_cat = HundredCategories.query.all()

    books_within_categories = [category.to_json() for category in hun_cat]
    return jsonify(books_within_categories)


@main.route('/thousand_categories')
@login_required
def view_books_thousand_categories():
    thou_cat = ThousandCategories.query.all()

    user = User.query.filter_by(username='john').first()
    books = user.books.all()

    books_within_categories = [category.to_json() for category in thou_cat]
    return jsonify(books_within_categories)



