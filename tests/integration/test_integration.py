import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from lambda_functions.process_csv.lambda_function import lambda_handler
import boto3

# Load .env.test for testing
@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv(dotenv_path=".env.test")

@pytest.fixture
def test_db_engine():
    test_db_url = os.getenv('DATABASE_URL_TEST')
    return create_engine(test_db_url)

def test_lambda_handler_integration(test_db_engine):
    # Setup AWS S3 client with test credentials
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

    # Name of the S3 bucket to use (can be a test bucket)
    bucket_name = "wrec-upload-book-csv"
    key = "user-csv/1/goodreads_library_export_sample.csv"

    # Create a mock event with the actual bucket name
    event = {
        "Records": [{
            "s3": {
                "bucket": {"name": bucket_name},
                "object": {"key": key}
            }
        }]
    }

    # Invoke lambda_handler
    response = lambda_handler(event, None)

    # Your test assertions go here
    assert response['statusCode'] == 200
    # Additional assertions to check data in the test database

    # Perform any cleanup if necessary
