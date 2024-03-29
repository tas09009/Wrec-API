import os
import re
import boto3
import csv
import chardet
import unicodedata
import sqlalchemy as sa
import psycopg2
from io import StringIO

s3_client = boto3.client('s3')

db_url = os.getenv('DATABASE_URL_TEST')
if not db_url:
    raise ValueError("DATABASE_URL environment variable not set")

def test_handler():
    # Use the detected encoding to decode the content
    book_data = [{'isbn': "isbn", 'title': "title", 'author': "author"}]
    with get_db_connection() as connection:
        process_book_data(book_data, connection)

    return {
        'statusCode': 200,
        'body': 'Processed books successfully'
    }


def get_db_connection():
    engine = sa.create_engine(db_url)
    print(f"engine: {engine}")
    connection = engine.connect()
    print(f"connection: {connection}")
    return connection

def lambda_handler(event, context):

    # bucket_name = "wrec-upload-book-csv"
    # file_key = "user-csv/1/goodreads_library_export_sample.csv" #TODO: remove hardcoded path
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']

    file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    file_content = file_obj['Body'].read()

    # Check for the encoding of the CSV content
    charset = chardet.detect(file_content)['encoding']

    # Use the detected encoding to decode the content
    dataFile = StringIO(file_content.decode(charset))
    csv_reader = csv.reader(dataFile)
    book_data = parse_csv_data(csv_reader)
    with get_db_connection() as connection:
        process_book_data(book_data, connection)

    return {
        'statusCode': 200,
        'body': 'Processed books successfully'
    }


def extract_number(value):
    # Use a regular expression to find digits in the string
    match = re.search(r'\d+', value)
    if match:
        return match.group()
    return None

def parse_csv_data(csv_reader):
    ISBN_10_IDX = 5
    ISBN_13_IDX = 6
    TITLE_IDX = 1
    AUTHOR_IDX = 2
    parsed_data = []

    # Skip the header row
    next(csv_reader, None)

    for row in csv_reader:
        isbn_10 = extract_number(row[ISBN_10_IDX])
        isbn_13 = extract_number(row[ISBN_13_IDX])
        isbn = isbn_10 or isbn_13
        author = unicodedata.normalize('NFD', row[AUTHOR_IDX]).encode('ascii', 'ignore').decode('utf-8')
        title = unicodedata.normalize('NFD', row[TITLE_IDX]).encode('ascii', 'ignore').decode('utf-8')

        parsed_data.append({'isbn': isbn, 'title': title, 'author': author})

    return parsed_data

def process_book_data(book_data, connection):
    for book in book_data:
        result = connection.execute(sa.text("SELECT * FROM books WHERE title = :title"), {'title': book['title']})
        existing_book = result.fetchone()
        print(f"existing book: {existing_book}")

        if not existing_book:
            insert_stmt = sa.text("""
                INSERT INTO books (isbn, title, author)
                VALUES (:isbn, :title, :author)
            """)
            connection.execute(insert_stmt, {'isbn': book['isbn'], 'title': book['title'], 'author': book['author']})
            connection.commit()
            print(f"Added book: {book['title']} | {book['author']} | {book['isbn']}")
