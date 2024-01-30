import os
from typing import Dict, List
import pytest
from sqlalchemy import create_engine, text
from lambda_functions.process_csv.lambda_function import process_book_data, parse_csv_data


@pytest.fixture
def test_engine():
    test_db_url = os.getenv('DATABASE_URL_TEST')
    print(f"test DB url: {test_db_url}")
    if not test_db_url:
        raise RuntimeError("DATABASE_URL_TEST environment variable not set")

    # Connect to the test database
    engine = create_engine(test_db_url)
    connection = engine.connect()

    # Start a transaction
    transaction = connection.begin()

    yield connection  # This is what the tests will use

    # Rollback the transaction after each test
    transaction.rollback()
    connection.close()



def test_process_book_data(sample_csv_data, test_engine):
    parsed_data: List[Dict] = parse_csv_data(sample_csv_data)

    # Process book data
    process_book_data(parsed_data, test_engine)

    # Assertions to check if the data is processed correctly
    for book in parsed_data:
        result = test_engine.execute(text("SELECT * FROM books WHERE title = :title"), {'title': book['title']})
        db_book = result.fetchone()
        print(db_book)

        print(f"Testing for book: {book['title']}")
        if db_book:
            print(f"Found in DB: {db_book[1]} | {db_book[2]} | {db_book[4]}")  # Access by index
        else:
            print("Not found in DB")

        assert db_book is not None
        assert db_book[1] == book['title']
        assert db_book[2] == book['author']
        assert db_book[4] == book['isbn']
