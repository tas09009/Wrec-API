import pytest
from lambda_functions.process_csv.lambda_function import parse_csv_data

def test_parse_csv_data(sample_csv_data):
    parsed_data = parse_csv_data(sample_csv_data)

    assert len(parsed_data) > 0
    assert parsed_data[0]['title'] == 'Kafka on the Shore'
    assert parsed_data[0]['author'] == 'Haruki Murakami'
    assert parsed_data[0]['isbn'] == '1400079276'

    # Test with a "None" ISBN value
    assert parsed_data[16]['title'] == 'The Picture of Dorian Gray'
    assert parsed_data[16]['author'] == 'Oscar Wilde'
    assert parsed_data[16]['isbn'] == None
