from flask import render_template, jsonify, request, url_for, redirect
from flask_login import login_required, current_user
from . import main
from .. import db
from app.models import Book, User, TenCategories, HundredCategories, ThousandCategories



@main.route('/')
def index():
    return render_template('index.html')

@main.route('/circlepacking') #TODO user isn't used in function
@login_required
def circle_packing_view():

    # user = User.query.filter_by(id=current_user.id).first()
    user_books = User.query.filter_by(id=current_user.id).first().books.all()

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

                # Add user's books only

                # tho_placeholder["children"] = []
                # for book in user_books:
                #     if book.classify_thousand_id == 


                tho_list.append(tho_placeholder)

        tens_list.append(ten_placeholder)
  
    return jsonify(books_dict)


@main.route('/bookshelf')
@login_required
def view_books_by_user():

    user_books = User.query.filter_by(id=current_user.id).first().books.all()

    books_list = [book.serialize() for book in user_books]
    return jsonify(books_list)

@main.route('/ten_categories')
@login_required
def view_books_ten_categories():
    user_books = User.query.filter_by(id=current_user.id).first().books.all()
    ten_cat = TenCategories.query.all()

    users_books_within_ten = []
    for category in ten_cat:
        classification = category.to_json()
        for book in user_books:
            if book.classify_ten_id == category.id:
                classification['books'].append(book.title)

        users_books_within_ten.append(classification)
    return jsonify(users_books_within_ten)


@main.route('/hundred_categories')
@login_required
def view_books_hundred_categories():

    user_books = User.query.filter_by(id=current_user.id).first().books.all()
    hun_cat = HundredCategories.query.all()

    users_books_within_ten = []
    for category in hun_cat:
        classification = category.to_json()
        for book in user_books:
            if book.classify_ten_id == category.id:
                classification['books'].append(book.title)

        users_books_within_ten.append(classification)
    return jsonify(users_books_within_ten)



@main.route('/thousand_categories')
@login_required
def view_books_thousand_categories():
    user_books = User.query.filter_by(id=current_user.id).first().books.all()
    thou_cat = ThousandCategories.query.all()

    users_books_within_ten = []
    for category in thou_cat:
        classification = category.to_json()
        for book in user_books:
            if book.classify_ten_id == category.id:
                classification['books'].append(book.title)

        users_books_within_ten.append(classification)
    return jsonify(users_books_within_ten)


