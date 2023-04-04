
import os
import csv

def generate_dewey_categories_blueprint():
    bookshelf_data = {
        "name": "Bookshelf",
        "children":[],
    }

    # csv --> json
    # {'0': {ten}, '1': {hundred}, '2': {thousand}}
    categories_json = {}
    file_name = 'externalFiles/dewey_classifications/DDSGORun{file}.csv'
    for i in range(0,3):
        file_path = file_name.format(file=str(i))
        with open(file_path, newline='') as f:
            reader = csv.reader(f)
            data_str_keys = dict(reader)
            data = {int(key): val for key, val in data_str_keys.items()}
            categories_json[str(i)] = data

    # populate only the ten categories - for now
    for key, val in categories_json['0'].items():
        level_ten = {"name": f"{key}: {val}", "children": []}
        bookshelf_data["children"].append(level_ten)

    # manually add the books
    book1 = {"name": "Trust", "value": 1}
    book2 = {"name": "Nothing to See Here", "value": 1}
    bookshelf_data["children"][8]["children"].append(book1)
    bookshelf_data["children"][8]["children"].append(book2)

    return bookshelf_data