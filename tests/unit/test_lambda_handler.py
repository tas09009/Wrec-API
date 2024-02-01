import boto3
import pytest
import os
from moto import mock_s3
from sqlalchemy import create_engine
from aws_wrec_lambda.handler import lambda_handler

"""Uses mock data - which is why it's considered a unit test, not an integration test"""


# Mock S3 setup
@pytest.fixture
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture
def s3_setup(aws_credentials):
    with mock_s3():
        conn = boto3.client("s3")
        bucket_name = "wrec-upload-book-csv"
        key = "user-csv/1/goodreads_library_export_sample.csv"

        # Create bucket and upload test object
        conn.create_bucket(Bucket=bucket_name)
        conn.put_object(Bucket=bucket_name, Key=key, Body="sample data")

        # Return the bucket name and key for use in tests
        yield {"bucket_name": bucket_name, "key": key}


# PostgreSQL setup
@pytest.fixture
def db_setup():
    engine = create_engine('postgresql://test_user:test_password@localhost:5432/test_db')
    yield engine

def test_lambda_s3_interaction(s3_setup, db_setup):
    bucket_name = s3_setup['bucket_name']
    key = s3_setup['key']

    # Create a mock event with the correct bucket name and key
    event = {
        "Records": [{
            "s3": {
                "bucket": {
                    "name": bucket_name
                },
                "object": {
                    "key": key
                }
            }
        }]
    }

    # Invoke lambda_handler
    response = lambda_handler(event, None)

    # Assert response and database entries
    assert response['statusCode'] == 200
    # Additional assertions to check data in PostgreSQL
