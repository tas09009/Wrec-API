from flask import render_template, jsonify
from flask_login import login_required, current_user
from . import main
from app.models import (
    User,
    TenCategories,
    HundredCategories,
    ThousandCategories,
)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/circlepacking")
@login_required
def circle_packing_view():

    user_books = User.query.filter_by(id=current_user.id).first().books.all()
    ten_cat = TenCategories.query.all()

    tens_list = []
    books_dict = {"name": "books", "children": tens_list}
    for i in ten_cat:
        ten_placeholder = {}
        hun_list = []
        ten_title = i.call_number + " | " + i.classification
        ten_placeholder["name"] = ten_title
        ten_placeholder["children"] = hun_list
        for j in i.hundred_values:
            hun_placeholder = {}
            tho_list = []
            hun_title = j.call_number + " | " + j.classification
            hun_placeholder["name"] = hun_title
            hun_placeholder["children"] = tho_list
            hun_list.append(hun_placeholder)
            for k in j.thousand_values:
                tho_placeholder = {}
                tho_title = k.call_number + " | " + k.classification
                tho_placeholder["name"] = tho_title
                tho_placeholder["children"] = []
                filtered_books = list(filter(lambda b: b.classify_thousand_id == k.id, user_books))
                filtered_books_titles = [i.title for i in filtered_books]
                tho_placeholder["children"].extend(filtered_books_titles)
                tho_list.append(tho_placeholder)
        tens_list.append(ten_placeholder)

    return jsonify(books_dict)


@main.route("/list_of_books")
@login_required
def view_books_by_user():
    user_books = User.query.filter_by(id=current_user.id).first().books.all()
    books_list = [book.serialize() for book in user_books]
    return jsonify(books_list)


@main.route("/ten_categories")
@login_required
def view_books_ten_categories():
    user_books = User.query.filter_by(id=current_user.id).first().books.all()
    ten_cat = TenCategories.query.all()

    users_books_within_ten = []
    for category in ten_cat:
        book_class = category.to_json()
        filtered_books = list(filter(lambda b: b.classify_ten_id == category.id, user_books))
        filtered_books_titles = [i.title for i in filtered_books]
        book_class["books"].extend(filtered_books_titles)

        users_books_within_ten.append(book_class)
    return jsonify(users_books_within_ten)


@main.route("/hundred_categories")
@login_required
def view_books_hundred_categories():
    user_books = User.query.filter_by(id=current_user.id).first().books.all()
    hun_cat = HundredCategories.query.all()

    users_books_within_ten = []
    for category in hun_cat:
        book_class = category.to_json()
        filtered_books = list(filter(lambda b: b.classify_hundred_id == category.id, user_books))
        filtered_books_titles = [i.title for i in filtered_books]
        book_class["books"].extend(filtered_books_titles)
        users_books_within_ten.append(book_class)
    return jsonify(users_books_within_ten)


@main.route("/thousand_categories")
@login_required
def view_books_thousand_categories():
    user_books = User.query.filter_by(id=current_user.id).first().books.all()
    thou_cat = ThousandCategories.query.all()

    users_books_within_ten = []
    for category in thou_cat:
        book_class = category.to_json()
        filtered_books = list(filter(lambda b: b.classify_thousand_id == category.id, user_books))
        filtered_books_titles = [i.title for i in filtered_books]
        book_class["books"].extend(filtered_books_titles)

        users_books_within_ten.append(book_class)
    return jsonify(users_books_within_ten)
