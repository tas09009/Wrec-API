import json
import boto3
from sqlalchemy import create_engine, text

test_db = "postgresql+psycopg2://seupapiy:4Ki4A2gKXs70TMb8xq_fXrJq8aJGmfGz@batyr.db.elephantsql.com/seupapiy"
db_engine = create_engine(test_db)

def hello(event, context):

    # TEST: DB connection
    with db_engine.connect() as connection:
        print(connection)

        query = text("SELECT * FROM books WHERE title=:title")
        result = connection.execute(query, {'title': 'Kafka on the Shore'})
        print(f'result: {result}')

        books = result.fetchall()
        print(f'books: {books}')

        # Add assertions based on what you expect to find in the database
        # print(f'books: {books}')
        assert len(books) > 0  # Example assertion


    body = {
        # "books": books,
        "input": event,
    }

    # TEST: S3 bucket
    bucket_name = "wrec-upload-book-csv"
    file_key = "user-csv/1/goodreads_library_export_sample.csv" #TODO: remove hardcoded path

    s3_client = boto3.client('s3')
    file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    file_content = file_obj['Body'].read()
    print(f'file_content: {file_content}')


    # # TEST: importing packages
    # try:
    #     import chardet
    #     print(f"The package {chardet.__name__} has been successfully imported.")
    #     import sqlalchemy
    #     print(f"The package {sqlalchemy.__name__} has been successfully imported.")
    # except ImportError:
    #     print("Failed to import the package.")

    return {"statusCode": 200, "body": json.dumps(body)}