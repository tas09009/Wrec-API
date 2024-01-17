import pytest
import csv
from io import StringIO

@pytest.fixture
def sample_csv_data():
    with open('tests/unit/data/goodreads_library_export_sample.csv', 'r', encoding='utf-8') as file:
        yield csv.reader(file)
