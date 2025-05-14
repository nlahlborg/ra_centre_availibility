"""
tests for functions in src/parser_utils.py
"""
#pylint: disable=import-error, wrong-import-position
from pathlib import Path
import sys
sys.path.insert(1, str(Path(__file__).parent.parent))
import pytest

from src.setup import API_TZ as TZ
from src.parser import (
    get_facility_type, parse_object_name, parse_data,
    parse_displayname, flag_inconsistant_datetime,
    flag_stale_start_datetime, DataValidationError
)
from tests.helpers.helper_constants import (
    GET_FACILITY_TYPE_TEST_CONSTANT, PARSE_OBJECT_NAME_TEST_CONSTANT,
    PARSE_DATA_TEST_CONSTANT, PARSE_DISPLAY_NAME_TEST_CONSTANT,
    FLAG_INCONSISTANT_DATETIME_TEST_CONSTANT,
    FLAG_STALE_START_DATETIME_TEST_CONSTANT
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

@pytest.mark.parametrize(
        "data,scraped_datetime,expected_facility_data,expected_timeslot_data,expected_event_data", 
        PARSE_DATA_TEST_CONSTANT
        )
def test_parse_data(
    data,
    scraped_datetime,
    expected_facility_data,
    expected_timeslot_data,
    expected_event_data
    ):
    """
    Test that parse data creates the right data structure
    """
    facility_data, timeslot_data, event_data = parse_data(data, scraped_datetime)

    assert facility_data == expected_facility_data
    assert timeslot_data == expected_timeslot_data
    assert event_data == expected_event_data

@pytest.mark.parametrize("display_name,year,expected", PARSE_DISPLAY_NAME_TEST_CONSTANT)
def test_parse_displayname(display_name, year, expected):
    """
    test the parser for the website displayname, used in data validation
    """
    result = parse_displayname(display_name, year)

    assert result.astimezone(TZ) == expected.astimezone(TZ)

@pytest.mark.parametrize("start_datetime,display_name,expected", FLAG_INCONSISTANT_DATETIME_TEST_CONSTANT)
def test_flag_inconsistant_datetime(start_datetime, display_name, expected):
    """
    tests validation for inconsistent datetime between different fields returned in api call
    """
    try:
        flag_inconsistant_datetime(start_datetime, display_name)

        assert expected
    except DataValidationError:
        assert expected == DataValidationError

@pytest.mark.parametrize("start_datetime,scraped_datetime,expected", FLAG_STALE_START_DATETIME_TEST_CONSTANT)
def test_flag_stale_start_datetime(start_datetime, scraped_datetime, expected):
    """
    tests validation for stale data in an api call
    """
    try:
        flag_stale_start_datetime(start_datetime, scraped_datetime)

        assert expected
    except DataValidationError:
        assert expected == DataValidationError
