"""
tests for functions in src/parser_utils.py
"""
#pylint: disable=import-error, wrong-import-position
from pathlib import Path
import sys
sys.path.insert(1, str(Path(__file__).parent.parent))
import pytest

from src.parser import get_facility_type, parse_object_name, parse_data
from tests.helpers.helper_constants import (
    GET_FACILITY_TYPE_TEST_CONSTANT, PARSE_OBJECT_NAME_TEST_CONSTANT,
    PARSE_DATA_TEST_CONSTANT
)

@pytest.mark.parametrize("facility_name,expected", GET_FACILITY_TYPE_TEST_CONSTANT)
def test_get_facility_type(facility_name, expected):
    """
    Test the regex in the get facility type function
    """
    facility_type = get_facility_type(facility_name)
    assert facility_type == expected

@pytest.mark.parametrize("object_name,prefix,expected", PARSE_OBJECT_NAME_TEST_CONSTANT)
def test_parse_object_name(object_name, prefix, expected):
    """
    Test string parsing in the get_parse_object_name funciton
    """
    datetime_value = parse_object_name(object_name, prefix)

    assert datetime_value == expected

@pytest.mark.parametrize("data,scraped_datetime,expected", PARSE_DATA_TEST_CONSTANT)
def test_parse_data(data, scraped_datetime, expected):
    """
    Test that parse data creates the right data structure
    """
    data, _ = parse_data(data, scraped_datetime)

    #have to pop the inserted_datetime from data since that results from datetime.now
    _ = data.pop("inserted_datetime")

    assert data == expected

if __name__ == "__main__":
    pass